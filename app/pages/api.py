from flask import g

from app.model.orm import (
    Project,
    Study,
    Experiment,
)

# TODO (2025-09-16) Test non-public study/experiment


def project_json(publicId):
    project = g.db_session.get_one(Project, publicId)

    return {
        'id': project.publicId,
        'name': project.name,
    }

def study_json(publicId):
    study = g.db_session.get_one(Study, publicId)

    return {
        'id': study.publicId,
        'name': study.name,
    }


def experiment_json(publicId):
    experiment = g.db_session.get_one(Experiment, publicId)

    return {
        'id': experiment.publicId,
        'name': experiment.name,
    }
