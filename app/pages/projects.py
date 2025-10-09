from flask import (
    g,
    render_template,
)

from app.model.orm import Project


def project_show_page(publicId):
    project = g.db_session.get_one(Project, publicId)

    return render_template("pages/projects/show.html", project=project)
