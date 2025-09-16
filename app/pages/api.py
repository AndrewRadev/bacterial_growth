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
        'studies': [
            {
                'id':   s.publicId,
                'name': s.name,
            }
            for s in project.studies
        ]
    }

def study_json(publicId):
    study = g.db_session.get_one(Study, publicId)

    data = {
        'id':   study.publicId,
        'name': study.name,
    }

    if study.isPublished:
        data['experiments'] = [
            {
                'id':   e.publicId,
                'name': e.name,
            }
            for e in study.experiments
        ]

    return data


def experiment_json(publicId):
    experiment = g.db_session.get_one(Experiment, publicId)

    if not experiment.study.isPublished:
        raise NotFound

    return {
        'id': experiment.publicId,
        'name': experiment.name,
    }
