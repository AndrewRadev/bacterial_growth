import io
import csv


def export_model_csv(db_session, study):
    buf = io.StringIO()
    writer = csv.DictWriter(
        buf,
        fieldnames=[
            'bioreplicate',
            'compartment',
            'subject_type',
            'subject_name',
            'model_type',
            'input_pointCount',
            'input_endTime',
            'y0',
            'mumax',
            'lag',
            'y0_lm',
            'K',
            'h0',
            'r2',
            'rss',
        ]
    )
    writer.writeheader()

    for modeling_result in study.modelingResults:
        if modeling_result.state != 'ready':
            continue

        measurement_context = modeling_result.measurementContext
        subject = measurement_context.get_subject(db_session)

        params = modeling_result.params

        writer.writerow({
            'bioreplicate': measurement_context.bioreplicate.name,
            'compartment':  measurement_context.compartment.name,
            'subject_type': measurement_context.subjectType,
            'subject_name': subject.name,
            'model_type':   modeling_result.model_name,
            # Inputs:
            'input_pointCount': params['inputs'].get('pointCount', None),
            'input_endTime':    params['inputs'].get('endTime', None),
            # Coefficients:
            'y0':    params['coefficients'].get('y0',    None),
            'mumax': params['coefficients'].get('mumax', None),
            'lag':   params['coefficients'].get('lag',   None),
            'y0_lm': params['coefficients'].get('y0_lm', None),
            'K':     params['coefficients'].get('K',     None),
            'h0':    params['coefficients'].get('h0',    None),
            # Fit:
            'r2':  params['fit'].get('r2',  None),
            'rss': params['fit'].get('rss', None),
        })

    return buf.getvalue().encode('utf-8')
