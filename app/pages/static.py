"""
Static pages: home, about
"""

from pathlib import Path
from datetime import datetime

from flask import render_template, g
import sqlalchemy as sql

from app.model.orm import (
    Experiment,
    Measurement,
    Metabolite,
    Strain,
    Study,
    StudyMetabolite,
    Taxon,
)


def static_home_page():
    study_count = g.db_session.scalars(
        sql.select(sql.func.count(Study.publicId))
        .where(Study.isPublished)
    ).one()

    experiment_count = g.db_session.scalars(
        sql.select(sql.func.count(sql.distinct(Experiment.publicId)))
        .join(Study)
        .where(Study.isPublished)
    ).one()

    measurement_count = g.db_session.scalars(
        sql.select(sql.func.count(sql.distinct(Measurement.id)))
        .join(Study)
        .where(Study.isPublished)
    ).one()

    taxa_count       = g.db_session.scalars(sql.select(sql.func.count(Taxon.id))).one()
    metabolite_count = g.db_session.scalars(sql.select(sql.func.count(Metabolite.id))).one()

    study_taxa_count = g.db_session.scalars(
        sql.select(sql.func.count(sql.distinct(Strain.NCBId)))
        .join(Study)
        .where(Study.isPublished)
    ).one()

    study_metabolite_count = g.db_session.scalars(
        sql.select(sql.func.count(sql.distinct(StudyMetabolite.chebi_id)))
        .join(Study)
        .where(Study.isPublished)
    ).one()

    last_ncbi_update = _read_timestamp_file('var/external_data/last_ncbi_update.txt')
    last_chebi_update = _read_timestamp_file('var/external_data/last_chebi_update.txt')

    return render_template(
        "pages/static/home.html",
        study_count=study_count,
        experiment_count=experiment_count,
        measurement_count=measurement_count,
        metabolite_count=metabolite_count,
        study_metabolite_count=study_metabolite_count,
        taxa_count=taxa_count,
        study_taxa_count=study_taxa_count,
        last_ncbi_update=last_ncbi_update,
        last_chebi_update=last_chebi_update,
    )


def static_about_page():
    return render_template("pages/static/about.html")


def _read_timestamp_file(path):
    timestamp = None
    timestamp_path = Path(path)

    if timestamp_path.exists():
        content = timestamp_path.read_text().strip()
        if content != '':
            timestamp = datetime.fromisoformat(content).strftime("%B %d, %Y")

    return timestamp
