import io
import csv


def export_model_csv(db_session, study, user=None):
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

        if not modeling_result.isPublished and not study.manageable_by_user(user):
            continue

        measurement_context = modeling_result.measurementContext
        subject = measurement_context.get_subject(db_session)

        params = modeling_result.params

        writer.writerow({
            'bioreplicate': measurement_context.bioreplicate.name,
            'compartment':  measurement_context.compartment.name,
            'subject_type': measurement_context.subjectType,
            'subject_name': measurement_context.subjectName,
            'model_type':   modeling_result.model_name,
            # Inputs:
            'input_pointCount': params.get('inputs', {}).get('pointCount', None),
            'input_endTime':    params.get('inputs', {}).get('endTime', None),
            # Coefficients:
            'y0':    params.get('coefficients', {}).get('y0',    None),
            'mumax': params.get('coefficients', {}).get('mumax', None),
            'lag':   params.get('coefficients', {}).get('lag',   None),
            'y0_lm': params.get('coefficients', {}).get('y0_lm', None),
            'K':     params.get('coefficients', {}).get('K',     None),
            'h0':    params.get('coefficients', {}).get('h0',    None),
            # Fit:
            'r2':  params.get('fit', {}).get('r2',  None),
            'rss': params.get('fit', {}).get('rss', None),
        })

    return buf.getvalue().encode('utf-8')
