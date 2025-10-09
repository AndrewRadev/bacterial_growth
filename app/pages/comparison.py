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

from app.model.orm import MeasurementContext
from app.view.forms.comparative_chart_form import ComparativeChartForm


def comparison_show_page():
    left_axis_ids  = _parse_comma_separated_request_ids('l')
    right_axis_ids = _parse_comma_separated_request_ids('r')

    if len(left_axis_ids) or len(right_axis_ids):
        context_ids = left_axis_ids + right_axis_ids
        data_source = "link"
    else:
        compare_data = _init_compare_data()
        context_ids = compare_data['contexts']
        data_source = "session"

    measurement_contexts = g.db_session.scalars(
        sql.select(MeasurementContext)
        .where(MeasurementContext.id.in_(context_ids))
    ).all()

    measurement_contexts_by_study = {
        s: list(mcs)
        for (s, mcs)
        in itertools.groupby(measurement_contexts, lambda mc: mc.study)
    }

    # TODO (2025-05-18) Convert time units between studies
    chart_form = ComparativeChartForm(
        g.db_session,
        'h',
        left_axis_ids=left_axis_ids,
        right_axis_ids=right_axis_ids,
    )

    return render_template(
        "pages/comparison/show.html",
        measurement_contexts_by_study=measurement_contexts_by_study,
        chart_form=chart_form,
        data_source=data_source,
    )


def comparison_update_json(action):
    compare_data = _init_compare_data()
    contexts     = request.json['contexts']
    context_set  = set(compare_data['contexts'])

    for context in contexts:
        if action == 'add':
            context_set.add(context)
        elif action == 'remove':
            context_set.discard(context)
        else:
            raise ValueError(f"Unexpected action: {action}")

    compare_data['contexts'] = list(context_set)
    session['compareData'] = compare_data

    return json.dumps({'contextCount': len(compare_data['contexts'])})


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
    chart = chart_form.build_chart(args, width, legend_position='top', clamp_x_data=True)

    return render_template(
        'pages/comparison/_chart.html',
        chart_form=chart_form,
        chart=chart,
    )


def _init_compare_data():
    data = session.get('compareData', {})

    if 'contexts' not in data:
        data['contexts'] = []

    return data


def _parse_comma_separated_request_ids(key):
    return [int(s) for s in request.args.get(key, '').split(',') if s != '']
