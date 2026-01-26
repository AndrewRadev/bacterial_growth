import re

from flask import (
    g,
    request,
)
from werkzeug.exceptions import NotFound
import sqlalchemy as sql

from app.model.orm import (
    Bioreplicate,
    Experiment,
    Measurement,
    MeasurementContext,
    Metabolite,
    Project,
    Study,
    StudyStrain,
)


def project_json(publicId):
    project = g.db_session.get_one(Project, publicId)

    return {
        'id': project.publicId,
        'name': project.name,
        'description': project.description,
        'studies': [
            {'id': s.publicId, 'name': s.name}
            for s in project.studies
        ]
    }


def study_json(publicId):
    study = g.db_session.get_one(Study, publicId)

    data = {
        'id':        study.publicId,
        'name':      study.name,
        'projectId': study.project.publicId,
    }

    if study.isPublished:
        data.update({
            'description': study.description,
            'url':         study.url,
            'uploadedAt':  study.createdAt.isoformat(),
            'publishedAt': study.publishedAt.isoformat(),
            'experiments': [
                {'id': e.publicId, 'name': e.name}
                for e in study.experiments
            ]
        })

    return data


def experiment_json(publicId):
    experiment = g.db_session.get_one(Experiment, publicId)

    if not experiment.study.isPublished:
        raise NotFound

    if experiment.community:
        community_strains = experiment.community.strains
    else:
        community_strains = []

    return {
        'id':              experiment.publicId,
        'name':            experiment.name,
        'description':     experiment.description,
        'studyId':         experiment.study.publicId,
        'cultivationMode': experiment.cultivationMode,

        'communityStrains': [
            {
                'id':     s.id,
                'NCBId':  s.ncbiId,
                'custom': not s.defined,
                'name':   s.name,
            } for s in community_strains
        ],

        'compartments': [
            {
                'name':                  c.name,
                'volume':                c.volume,
                'pressure':              c.pressure,
                'stirringSpeed':         c.stirringSpeed,
                'stirringMode':          c.stirringMode,
                'O2':                    c.O2,
                'CO2':                   c.CO2,
                'H2':                    c.H2,
                'N2':                    c.N2,
                'inoculumConcentration': c.inoculumConcentration,
                'inoculumVolume':        c.inoculumVolume,
                'initialPh':             c.initialPh,
                'dilutionRate':          c.dilutionRate,
                'initialTemperature':    c.initialTemperature,
                'mediumName':            c.mediumName,
                'mediumUrl':             c.mediumUrl,
            }
            for c in experiment.compartments
        ],

        'bioreplicates': [
            {
                'id':                  b.id,
                'name':                b.name,
                'biosampleUrl':        b.biosampleUrl,
                'measurementContexts': [
                    {
                        'id': mc.id,
                        **_measurement_technique_fields(mc.technique),
                        **_measurement_subject_fields(mc)
                    }
                    for mc in b.measurementContexts
                ]
            }
            for b in experiment.bioreplicates
        ]
    }


def experiment_csv(publicId):
    experiment = g.db_session.get(Experiment, publicId)
    if not experiment or not experiment.study.isPublished:
        raise NotFound

    df = experiment.get_df(g.db_session)

    return df.to_csv(index=False)


def measurement_context_json(id):
    measurement_context = g.db_session.get(MeasurementContext, id)
    if not measurement_context or not measurement_context.study.isPublished:
        raise NotFound

    measurement_count = g.db_session.scalars(
        sql.select(sql.func.count(Measurement.id))
        .where(Measurement.contextId == measurement_context.id)
    ).one()

    return {
        'id':                   measurement_context.id,
        'experimentId':         measurement_context.bioreplicate.experimentId,
        'studyId':              measurement_context.studyId,
        'bioreplicateId':       measurement_context.bioreplicate.id,
        'bioreplicateName':     measurement_context.bioreplicate.name,
        **_measurement_technique_fields(measurement_context.technique),
        **_measurement_subject_fields(measurement_context),
        'measurementCount':     measurement_count,
        'measurementTimeUnits': 'h',
    }


def measurement_context_csv(id):
    measurement_context = g.db_session.get(MeasurementContext, id)
    if not measurement_context or not measurement_context.study.isPublished:
        raise NotFound

    df = measurement_context.get_df(g.db_session)

    if request.args.get('withLabel'):
        html_label = measurement_context.get_chart_label()
        plain_label = re.sub(r'</?(b|sub)>', '', html_label)

        df.rename(columns={'value': plain_label}, inplace=True)

    return df.to_csv(index=False)


def bioreplicate_json(id):
    bioreplicate = g.db_session.get(Bioreplicate, id)
    if not bioreplicate or not bioreplicate.study.isPublished:
        raise NotFound

    return {
        'id':                   bioreplicate.id,
        'experimentId':         bioreplicate.experiment.publicId,
        'studyId':              bioreplicate.experiment.studyId,
        'name':                 bioreplicate.name,
        'biosampleUrl':         bioreplicate.biosampleUrl,
        'measurementTimeUnits': 'h',
        'measurementContexts': [
            {
                'id': mc.id,
                **_measurement_technique_fields(mc.technique),
                **_measurement_subject_fields(mc),
            }
            for mc in bioreplicate.measurementContexts
        ]
    }


def bioreplicate_csv(id):
    bioreplicate = g.db_session.get(Bioreplicate, id)
    if not bioreplicate or not bioreplicate.study.isPublished:
        raise NotFound

    df = bioreplicate.get_df(g.db_session)

    return df.to_csv(index=False)


def search_json():
    request_args = request.args.to_dict()
    if len(request_args) == 0:
        return {"error": "No search query parameters"}, 400

    results = set()

    for (key, value) in request_args.items():
        if key == 'strainNcbiIds':
            values = value.split(',')
            study_strain_ids = g.db_session.scalars(
                sql.select(StudyStrain.id)
                .where(StudyStrain.ncbiId.in_(values)),
            ).all()
            results.update(_contexts_by_subject('strain', study_strain_ids))

        elif key == 'metaboliteChebiIds':
            values = [f"CHEBI:{v}" for v in value.split(',')]

            metabolite_ids = g.db_session.scalars(
                sql.select(Metabolite.id)
                .where(Metabolite.chebiId.in_(values)),
            ).all()
            results.update(_contexts_by_subject('metabolite', metabolite_ids))

        else:
            return {"error": f"Unknown search parameter: {key}"}, 400

    measurement_contexts = list(results)

    experiment_ids = sorted({mc.experiment.publicId for mc in measurement_contexts})
    study_ids      = sorted({mc.experiment.studyId for mc in measurement_contexts})

    return {
        'studies':              study_ids,
        'experiments':          experiment_ids,
        'measurementTimeUnits': 'h',
        'measurementContexts': [
            {
                'id':               mc.id,
                'experimentId':     mc.experiment.publicId,
                'studyId':          mc.studyId,
                'bioreplicateId':   mc.bioreplicate.id,
                'bioreplicateName': mc.bioreplicate.name,
                **_measurement_technique_fields(mc.technique),
                **_measurement_subject_fields(mc),
            }
            for mc in measurement_contexts
        ]
    }


def _measurement_technique_fields(measurement_technique):
    fields = {
        'techniqueType':  measurement_technique.type,
        'techniqueUnits': measurement_technique.units,
    }
    if cell_type := measurement_technique.cellType:
        fields['techniqueCellType'] = cell_type

    return fields


def _measurement_subject_fields(measurement_context):
    subject_type = measurement_context.subjectType
    subject_name = measurement_context.subjectName
    extra_data = {}

    if measurement_context.subjectExternalId:
        if subject_type == 'strain':
            external_id = int(measurement_context.subjectExternalId.removeprefix('NCBI:'))
            extra_data = {'NCBId': external_id}
        elif subject_type == 'metabolite':
            external_id = int(measurement_context.subjectExternalId.removeprefix('CHEBI:'))
            extra_data = {'chebiId': external_id}

    return {
        'subject': {
            'type': subject_type,
            'name': subject_name,
            **extra_data,
        }
    }


def _contexts_by_subject(subject_type, subject_id):
    sql_options = (
        sql.orm.joinedload(MeasurementContext.technique),
        sql.orm.joinedload(MeasurementContext.experiment),
    )

    if isinstance(subject_id, list):
        return g.db_session.scalars(
            sql.select(MeasurementContext)
            .where(
                MeasurementContext.subjectType == subject_type,
                MeasurementContext.subjectId.in_(subject_id),
            )
            .options(*sql_options)
        ).all()
    else:
        return g.db_session.scalars(
            sql.select(MeasurementContext)
            .where(
                MeasurementContext.subjectType == subject_type,
                MeasurementContext.subjectId == subject_id,
            )
            .options(*sql_options)
        ).all()
