import json
import itertools

from flask import (
    g,
    render_template,
    redirect,
    request,
    session,
)
import sqlalchemy as sql

from app.model.orm import MeasurementContext, ModelingResult
from app.view.forms.comparative_chart_form import ComparativeChartForm


def comparison_show_page():
    left_axis_ids  = _parse_comma_separated_request_ids('l')
    right_axis_ids = _parse_comma_separated_request_ids('r')

    left_axis_model_ids  = _parse_comma_separated_request_ids('lm')
    right_axis_model_ids = _parse_comma_separated_request_ids('rm')

    if len(left_axis_ids) + len(right_axis_ids) + len(left_axis_model_ids) + len(right_axis_model_ids) > 0:
        context_ids = left_axis_ids + right_axis_ids
        model_ids = left_axis_model_ids + right_axis_model_ids
        data_source = "link"
    else:
        compare_data = _init_compare_data()
        context_ids = compare_data['contexts']
        model_ids = compare_data['models']
        data_source = "session"

    measurement_contexts = g.db_session.scalars(
        sql.select(MeasurementContext)
        .where(MeasurementContext.id.in_(context_ids))
    ).all()

    modeling_results = g.db_session.scalars(
        sql.select(ModelingResult)
        .where(ModelingResult.id.in_(model_ids))
    ).all()

    study_set = {
        *map(lambda mc: mc.study, measurement_contexts),
        *map(lambda mr: mr.study, modeling_results),
    }

    records_by_study = {}

    for study, measurement_context_group in itertools.groupby(measurement_contexts, lambda mc: mc.study):
        if study not in records_by_study:
            records_by_study[study] = {'measurement_contexts': [], 'modeling_results': []}
        records_by_study[study]['measurement_contexts'] = list(measurement_context_group)

    for study, modeling_result_group in itertools.groupby(modeling_results, lambda mc: mc.study):
        if study not in records_by_study:
            records_by_study[study] = {'measurement_contexts': [], 'modeling_results': []}
        records_by_study[study]['modeling_results'] = list(modeling_result_group)

    # TODO (2025-05-18) Convert time units between studies
    chart_form = ComparativeChartForm(
        g.db_session,
        'h',
        left_axis_ids=left_axis_ids,
        right_axis_ids=right_axis_ids,
        left_axis_model_ids=left_axis_model_ids,
        right_axis_model_ids=right_axis_model_ids,
    )

    return render_template(
        "pages/comparison/show.html",
        records_by_study=records_by_study,
        chart_form=chart_form,
        data_source=data_source,
    )


def comparison_update_json(action):
    compare_data = _init_compare_data()

    context_set = set(compare_data['contexts'])
    model_set   = set(compare_data['models'])

    for context in request.json.get('contexts', []):
        if action == 'add':
            context_set.add(context)
        elif action == 'remove':
            context_set.discard(context)
        else:
            raise ValueError(f"Unexpected action: {action}")

    for model in request.json.get('models', []):
        if action == 'add':
            model_set.add(model)
        elif action == 'remove':
            model_set.discard(model)
        else:
            raise ValueError(f"Unexpected action: {action}")

    compare_data['contexts'] = list(context_set)
    compare_data['models'] = list(model_set)

    session['compareData'] = compare_data

    return json.dumps({
        'contextCount': len(compare_data['contexts']),
        'modelCount':   len(compare_data['models']),
    })


def comparison_clear_action():
    if 'compareData' in session:
        del session['compareData']

    return redirect(request.referrer)


def comparison_chart_fragment():
    args = request.form.to_dict()
    width = request.args.get('width', None)

    # TODO (2025-05-18) Convert time units between studies
    chart_form = ComparativeChartForm(
        g.db_session,
        time_units='h',
        show_std=args.get('showStd', None) is not None,
        show_perturbations=args.get('showPerturbations', None) is not None,
    )
    chart = chart_form.build_chart(args, width, clamp_x_data=True)

    return render_template(
        'pages/comparison/_chart.html',
        chart_form=chart_form,
        chart=chart,
    )


def _init_compare_data():
    data = session.get('compareData', {})

    if 'contexts' not in data:
        data['contexts'] = []
    if 'models' not in data:
        data['models'] = []

    return data


def _parse_comma_separated_request_ids(key):
    return [int(s) for s in request.args.get(key, '').split(',') if s != '']
