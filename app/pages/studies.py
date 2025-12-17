import uuid

from flask import (
    g,
    render_template,
    send_file,
    request,
    redirect,
)
from werkzeug.exceptions import Forbidden
import sqlalchemy as sql

from app.model.orm import (
    Bioreplicate,
    Community,
    Experiment,
    MeasurementContext,
    Study,
    StudyUser,
    Submission,
)
from app.view.forms.experiment_export_form import ExperimentExportForm
from app.view.forms.comparative_chart_form import ComparativeChartForm
import app.model.lib.util as util


def study_show_page(publicId):
    study = _fetch_study_for_visitor(
        publicId,
        check_user_visibility=False,
        sql_options=(
            # Level 1:
            sql.orm.selectinload(Study.experiments, Experiment.compartments),
            sql.orm.selectinload(Study.experiments, Experiment.community),
            sql.orm.selectinload(Study.experiments, Experiment.perturbations),
            sql.orm.selectinload(Study.experiments, Experiment.bioreplicates),
            # Level 2:
            sql.orm.selectinload(Study.experiments, Experiment.community, Community.strains),
            sql.orm.selectinload(Study.experiments, Experiment.bioreplicates, Bioreplicate.measurementContexts),
            # Level 3:
            sql.orm.selectinload(
                Study.experiments,
                Experiment.bioreplicates,
                Bioreplicate.measurementContexts,
                MeasurementContext.measurements,
            ),
            sql.orm.selectinload(
                Study.experiments,
                Experiment.bioreplicates,
                Bioreplicate.measurementContexts,
                MeasurementContext.technique,
            ),
            sql.orm.selectinload(
                Study.experiments,
                Experiment.bioreplicates,
                Bioreplicate.measurementContexts,
                MeasurementContext.modelingResults,
            ),
        )
    )

    if study.visible_to_user(g.current_user):
        return render_template("pages/studies/show.html", study=study)
    else:
        return render_template("pages/studies/show_unpublished.html", study=study)


def study_manage_page(publicId):
    study = _fetch_study_for_visitor(publicId)
    if not study.manageable_by_user(g.current_user):
        raise Forbidden()

    return render_template("pages/studies/manage.html", study=study)


def study_export_page(publicId):
    study = _fetch_study_for_visitor(publicId)

    return render_template(
        "pages/studies/export.html",
        study=study,
        studyId=publicId,
    )


def study_export_preview_fragment(publicId):
    # We only need the id here, but we call it to apply visibility checks:
    _fetch_study_for_visitor(publicId)

    csv_previews = []
    export_form = ExperimentExportForm(g.db_session, request.args)
    experiment_data = export_form.get_experiment_data()

    for experiment, experiment_df in experiment_data.items():
        csv = experiment_df[:5].to_csv(index=False, sep=export_form.csv_separator)
        csv_previews.append(f"""
            <h3>{experiment.name}.csv ({len(experiment_df)} rows)</h3>
            <pre>{csv}</pre>
        """)

    return '\n'.join(csv_previews)


def study_download_data_zip(publicId):
    study = _fetch_study_for_visitor(publicId)
    csv_data = []

    export_form = ExperimentExportForm(g.db_session, request.args)
    experiment_data = export_form.get_experiment_data()

    for experiment, experiment_df in experiment_data.items():
        csv_bytes = experiment_df.to_csv(index=False, sep=export_form.csv_separator)
        csv_name = f"{experiment.name}.csv"

        csv_data.append((csv_name, csv_bytes))

    readme_text = render_template(
        'pages/studies/export_readme.md',
        study=study,
        experiments=experiment_data.keys(),
    )

    csv_data.append(('README.md', readme_text.encode('utf-8')))

    zip_file = util.createzip(csv_data)

    return send_file(
        zip_file,
        as_attachment=True,
        download_name=f"{publicId}.zip",
    )


def study_reset_action(publicId):
    study = _fetch_study_for_visitor(publicId, check_user_visibility=False)
    if study.ownerUuid != g.current_user.uuid:
        raise Forbidden()

    study_submissions = g.db_session.scalars(
        sql.select(Submission)
        .where(Submission.studyUniqueID == study.uuid)
    ).all()

    study.uuid = str(uuid.uuid4())

    g.db_session.add(study)
    g.db_session.add(StudyUser(
        user=g.current_user,
        study=study,
    ))

    for submission in study_submissions:
        submission.studyUniqueID = study.uuid
        g.db_session.add(submission)

    g.db_session.commit()

    return redirect(request.referrer)


def study_visualize_page(publicId):
    study = _fetch_study_for_visitor(publicId)

    left_axis_ids  = _parse_comma_separated_request_ids('l')
    right_axis_ids = _parse_comma_separated_request_ids('r')

    left_axis_model_ids  = _parse_comma_separated_request_ids('lm')
    right_axis_model_ids = _parse_comma_separated_request_ids('rm')

    chart_form = ComparativeChartForm(
        g.db_session,
        time_units=study.timeUnits,
        left_axis_ids=left_axis_ids,
        right_axis_ids=right_axis_ids,
        left_axis_model_ids=left_axis_model_ids,
        right_axis_model_ids=right_axis_model_ids,
    )

    return render_template(
        "pages/studies/visualize.html",
        study=study,
        chart_form=chart_form,
    )


def study_chart_fragment(publicId):
    study = _fetch_study_for_visitor(publicId)
    args = request.form.to_dict()

    width = request.args.get('width', None)

    chart_form = ComparativeChartForm(
        g.db_session,
        time_units=study.timeUnits,
        show_std=args.get('showStd', None) is not None,
        show_perturbations=args.get('showPerturbations', None) is not None,
    )
    chart = chart_form.build_chart(args, width)

    return render_template(
        'pages/studies/visualize/_chart.html',
        chart_form=chart_form,
        chart=chart,
        study=study,
    )


def _fetch_study_for_visitor(publicId, check_user_visibility=True, sql_options=None):
    sql_options = sql_options or ()

    study = g.db_session.scalars(
        sql.select(Study)
        .where(Study.publicId == publicId)
        .options(*sql_options)
        .limit(1)
    ).one()

    if check_user_visibility and not study.visible_to_user(g.current_user):
        raise Forbidden()

    return study


def _parse_comma_separated_request_ids(key):
    return [int(s) for s in request.args.get(key, '').split(',') if s != '']
