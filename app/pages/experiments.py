from flask import (
    g,
    render_template,
)
from werkzeug.exceptions import Forbidden

from app.model.orm import Experiment


def experiment_show_page(publicId):
    experiment = _fetch_experiment(publicId)

    return render_template("pages/experiments/show.html", experiment=experiment)


def _fetch_experiment(publicId):
    experiment = g.db_session.get(Experiment, publicId)

    if not experiment.study.visible_to_user(g.current_user):
        raise Forbidden()

    return experiment
