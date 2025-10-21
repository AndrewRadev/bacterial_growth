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
    Strain,
    Study,
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
                'NCBId': s.NCBId,
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
                        'id':             mc.id,
                        'techniqueType':  mc.technique.type,
                        'techniqueUnits': mc.technique.units,
                        'subject':        _render_measurement_subject(mc),
                    }
                    for mc in b.measurementContexts
                ]
            }
            for b in experiment.bioreplicates
        ]
    }


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
        'bioreplicateName':     measurement_context.bioreplicate.name,
        'techniqueType':        measurement_context.technique.type,
        'techniqueUnits':       measurement_context.technique.units,
        'subject':              _render_measurement_subject(measurement_context),
        'measurementCount':     measurement_count,
        'measurementTimeUnits': 'h',
    }


def measurement_context_csv(id):
    measurement_context = g.db_session.get(MeasurementContext, id)
    if not measurement_context or not measurement_context.study.isPublished:
        raise NotFound

    df = measurement_context.get_df(g.db_session)

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
                'id':             mc.id,
                'techniqueType':  mc.technique.type,
                'techniqueUnits': mc.technique.units,
                'subject':        _render_measurement_subject(mc),
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
        if key == 'strainNcbiId':
            study_strain_ids = g.db_session.scalars(
                sql.select(Strain.id)
                .where(Strain.NCBId == value),
            ).all()
            results.update(_contexts_by_subject('strain', study_strain_ids))

        elif key == 'metaboliteChebiId':
            if not value.startswith('CHEBI:'):
                value = f"CHEBI:{value}"

            metabolite = g.db_session.scalars(
                sql.select(Metabolite)
                .where(Metabolite.chebiId == value),
            ).one()
            results.update(_contexts_by_subject('metabolite', metabolite.id))

        else:
            return {"error": f"Unknown search parameter: {key}"}, 400

    measurement_contexts    = list(results)
    measurement_context_ids = [mc.id for mc in measurement_contexts]

    experiment_ids = sorted({mc.experiment.publicId for mc in measurement_contexts})
    study_ids      = sorted({mc.experiment.studyId for mc in measurement_contexts})

    return {
        'studies':              study_ids,
        'experiments':          experiment_ids,
        'measurementTimeUnits': 'h',
        'measurementContexts': [
            {
                'id':             mc.id,
                'experimentId':   mc.experiment.publicId,
                'studyId':        mc.studyId,
                'techniqueType':  mc.technique.type,
                'techniqueUnits': mc.technique.units,
                'subject':        _render_measurement_subject(mc),
            }
            for mc in measurement_contexts
        ]
    }


def _render_measurement_subject(measurement_context):
    subject = measurement_context.get_subject(g.db_session)
    subject_type = measurement_context.subjectType

    if subject_type == 'strain':
        extra_data = {'NCBId': subject.NCBId}
    elif subject_type == 'metabolite':
        extra_data = {'chebiId': int(subject.chebiId.removeprefix('CHEBI:'))}
    else:
        extra_data = {}

    return {
        'type': subject_type,
        'name': subject.name,
        **extra_data,
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
