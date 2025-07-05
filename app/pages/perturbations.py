import sqlalchemy as sql
from flask import (
    g,
    render_template,
)
from werkzeug.exceptions import Forbidden

from app.model.orm import Perturbation


def perturbation_show_page(id):
    perturbation = _fetch_perturbation(id)

    return render_template(
        "pages/perturbations/show.html",
        perturbation=perturbation,
    )


def _fetch_perturbation(id):
    perturbation = g.db_session.get_one(Perturbation, id)

    if not perturbation.study.visible_to_user(g.current_user):
        raise Forbidden()

    return perturbation
