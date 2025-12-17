import io
from datetime import datetime, UTC

from flask import (
    g,
    render_template,
    send_file,
    request,
    redirect,
    url_for,
)
from werkzeug.exceptions import Forbidden
import sqlalchemy as sql
import pandas as pd
import numpy as np

from app.model.orm import (
    CustomModel,
    Experiment,
    MeasurementContext,
    MeasurementTechnique,
    ModelingResult,
    Study,
    StudyTechnique,
)
from app.model.lib.chart import Chart
from app.model.lib.modeling_tasks import process_modeling_request
from app.model.lib.model_export import export_model_csv


def modeling_page(publicId):
    study = _fetch_study_for_manager(
        publicId,
        sql_options=(
            # Level 1:
            sql.orm.selectinload(Study.experiments, Experiment.bioreplicates),
            sql.orm.selectinload(Study.experiments, Experiment.compartments),
            sql.orm.selectinload(Study.studyTechniques, StudyTechnique.measurementTechniques),
            # Level 2:
            sql.orm.selectinload(
                Study.studyTechniques,
                StudyTechnique.measurementTechniques,
                MeasurementTechnique.measurementContexts,
            ),
            # Level 3:
            sql.orm.selectinload(
                Study.studyTechniques,
                StudyTechnique.measurementTechniques,
                MeasurementTechnique.measurementContexts,
                MeasurementContext.modelingResults,
            ),
        )
    )
    if not study.manageable_by_user(g.current_user):
        raise Forbidden()

    return render_template("pages/modeling/show.html", study=study)


def modeling_params_csv(publicId):
    study = _fetch_study_for_manager(publicId)

    csv_data = export_model_csv(g.db_session, study, g.current_user)

    return send_file(
        io.BytesIO(csv_data),
        as_attachment=True,
        download_name=f"{publicId}_models.csv",
    )


def modeling_submit_action(publicId):
    study = _fetch_study_for_manager(publicId)
    if not study.manageable_by_user(g.current_user):
        raise Forbidden()

    args = request.form.to_dict()

    modeling_type = args.pop('modelingType')
    measurement_context_id = int(args.pop('selectedContext').removeprefix('measurementContext|'))

    modeling_result = g.db_session.scalars(
        sql.select(ModelingResult)
        .where(
            ModelingResult.type == modeling_type,
            ModelingResult.measurementContextId == measurement_context_id,
        )
    ).one_or_none()

    if modeling_result is None:
        modeling_result = ModelingResult(
            type=modeling_type,
            measurementContextId=measurement_context_id,
        )

    modeling_result.state = 'pending'
    g.db_session.add(modeling_result)
    g.db_session.commit()

    process_modeling_request.delay(modeling_result.id, measurement_context_id, args)

    return {'modelingResultId': modeling_result.id}


def modeling_chart_fragment(publicId, measurementContextId):
    study = _fetch_study_for_manager(publicId)
    if not study.manageable_by_user(g.current_user):
        raise Forbidden()

    args = request.args.to_dict()

    modeling_type = args.pop('modelingType')
    log_transform = args.pop('logTransform', 'false') == 'true'

    measurement_context = g.db_session.get(MeasurementContext, measurementContextId)
    measurement_df      = measurement_context.get_df(g.db_session)

    chart = Chart(
        time_units=study.timeUnits,
        title=measurement_context.get_chart_label(),
        legend_position='right',
        log_left=log_transform,
    )
    units = measurement_context.technique.units
    if units == '':
        units = measurement_context.technique.short_name

    chart.add_df(
        measurement_df,
        units=units,
        label="Measurements",
    )

    modeling_record = g.db_session.scalars(
        sql.select(ModelingResult)
        .where(
            ModelingResult.type == modeling_type,
            ModelingResult.measurementContextId == measurement_context.id,
            ModelingResult.state == 'ready',
        )
    ).one_or_none()

    if modeling_record:
        df = modeling_record.generate_chart_df(measurement_df)

        label = modeling_record.model_name
        chart.add_model_df(df, units=units, label=label)

        model_params = modeling_record.params
        r_summary    = modeling_record.rSummary
    else:
        model_params = ModelingResult.empty_params(modeling_type)
        r_summary    = None

    return render_template(
        'pages/modeling/_chart.html',
        study_id=publicId,
        chart=chart,
        modeling_record=modeling_record,
        form_data=request.form,
        modeling_type=modeling_type,
        model_params=model_params,
        r_summary=r_summary,
        measurement_context=measurement_context,
        log_transform=log_transform,
    )


def modeling_toggle_published_action(publicId, modelingResultId):
    study = _fetch_study_for_manager(publicId)
    if not study.manageable_by_user(g.current_user):
        raise Forbidden()

    modeling_record = g.db_session.get(ModelingResult, modelingResultId)

    if modeling_record.isPublished:
        modeling_record.publishedAt = None
        g.db_session.add(modeling_record)
        g.db_session.commit()
    else:
        modeling_record.publishedAt = datetime.now(UTC)
        g.db_session.add(modeling_record)
        g.db_session.commit()

    return {}


def modeling_check_json(publicId):
    study = _fetch_study_for_manager(publicId)
    if not study.manageable_by_user(g.current_user):
        raise Forbidden()

    result_states = {}

    for modeling_result in study.modelingResults:
        result_states[modeling_result.id] = modeling_result.state

    return result_states


def modeling_custom_model_update_action(publicId):
    study = _fetch_study_for_manager(publicId)
    if not study.manageable_by_user(g.current_user):
        raise Forbidden()

    custom_model_id        = request.form.get('customModelId')
    measurement_context_id = request.form.get('selectedMeasurementContextId')

    technique_id = None
    if measurement_context_id:
        measurement_context = g.db_session.get(
            MeasurementContext,
            measurement_context_id,
        )

        if measurement_context:
            technique_id = measurement_context.techniqueId

    if custom_model_id:
        custom_model = g.db_session.get(CustomModel, custom_model_id)
        if custom_model.studyId != publicId:
            raise Forbidden
    else:
        custom_model = CustomModel(studyId=study.publicId)

    custom_model.update(
        name=request.form['name'],
        shortName=request.form['shortName'],
        url=request.form['url'],
        description=request.form['description'],
    )
    g.db_session.add(custom_model)
    g.db_session.commit()

    redirect_url = url_for(
        'modeling_page',
        publicId=study.publicId,
        selectedMeasurementContextId=measurement_context_id,
        selectedTechniqueId=technique_id,
        selectedCustomModelId=custom_model.id,
    )

    return redirect(redirect_url)


def modeling_custom_model_delete_action(publicId, customModelId):
    study = _fetch_study_for_manager(publicId)
    if not study.manageable_by_user(g.current_user):
        raise Forbidden()

    custom_model = g.db_session.get(CustomModel, customModelId)
    if custom_model.studyId != publicId:
        raise Forbidden

    g.db_session.delete(custom_model)
    g.db_session.commit()

    # The ajax action will reload the page
    return {}


def modeling_custom_model_upload_action(publicId, customModelId):
    study = _fetch_study_for_manager(publicId)
    if not study.manageable_by_user(g.current_user):
        raise Forbidden()

    measurement_context_id = request.form['selectedMeasurementContextId']

    custom_model = g.db_session.get_one(CustomModel, customModelId)
    if custom_model.studyId != publicId:
        raise Forbidden

    predictions_df = pd.read_csv(request.files['predictions'])

    modeling_result = g.db_session.scalars(
        sql.select(ModelingResult)
        .where(
            ModelingResult.measurementContextId == measurement_context_id,
            ModelingResult.customModelId == custom_model.id,
        )
    ).one_or_none()

    if modeling_result is None:
        modeling_result = ModelingResult(
            measurementContextId=request.form['selectedMeasurementContextId'],
            customModelId=custom_model.id,
            type=f"custom_{custom_model.id}",
            state='ready',
        )

    modeling_result.update(
        xValues=predictions_df['time'].tolist(),
        yValues=predictions_df['value'].tolist(),
    )

    if 'error' in predictions_df:
        modeling_result.yErrors = predictions_df['error'].replace({np.nan: None}).tolist(),

    g.db_session.add(modeling_result)
    g.db_session.commit()

    redirect_url = url_for(
        'modeling_page',
        publicId=study.publicId,
        selectedExperimentId=modeling_result.measurementContext.bioreplicate.experimentId,
        selectedMeasurementContextId=modeling_result.measurementContext.id,
        selectedTechniqueId=modeling_result.measurementContext.technique.id,
        selectedCustomModelId=custom_model.id,
    )

    return redirect(redirect_url)


def _fetch_study_for_manager(publicId, sql_options=None):
    sql_options = sql_options or ()

    study = g.db_session.scalars(
        sql.select(Study)
        .where(Study.publicId == publicId)
        .options(*sql_options)
        .limit(1)
    ).one()

    if not study.manageable_by_user(g.current_user):
        raise Forbidden()

    return study
