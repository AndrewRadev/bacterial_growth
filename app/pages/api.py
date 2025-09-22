from flask import g
from werkzeug.exceptions import NotFound

from app.model.orm import (
    Project,
    Study,
    Experiment,
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
            'timeUnits':   study.timeUnits,
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

    return {
        'id':          experiment.publicId,
        'name':        experiment.name,
        'description': experiment.description,
        'studyId':     experiment.study.publicId,
        'cultivationMode': experiment.cultivationMode,
        'community': {
            'id':   experiment.community.id,
            'name': experiment.community.name,
        },
        'compartments': [
            {'id': c.id, 'name': c.name}
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
                        'subject': {
                            'type': mc.subjectType,
                            'id':   mc.subjectId,
                        },
                    }
                    for mc in b.measurementContexts
                ]
            }
            for b in experiment.bioreplicates
        ]
    }
