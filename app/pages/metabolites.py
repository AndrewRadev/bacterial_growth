import json

from flask import request, g, render_template, url_for
import sqlalchemy as sql

from db import get_connection
from app.model.orm import Metabolite, StudyMetabolite
from app.model.lib.util import read_timestamp_date


def metabolite_show_page(chebiId):
    metabolite = g.db_session.scalars(
        sql.select(Metabolite)
        .where(Metabolite.chebiId == chebiId)
        .limit(1)
    ).one()

    study_count = g.db_session.scalars(
        sql.select(sql.func.count(StudyMetabolite.id))
        .where(StudyMetabolite.chebiId == metabolite.chebiId)
    ).one()

    search_url = url_for('search_index_page', chebiIds=metabolite.chebiId)

    last_chebi_update = read_timestamp_date('var/external_data/last_chebi_update.txt')

    return render_template(
        'pages/metabolites/show.html',
        metabolite=metabolite,
        study_count=study_count,
        search_url=search_url,
        last_chebi_update=last_chebi_update,
    )


def metabolites_completion_json():
    term         = request.args.get('term', '')
    page         = int(request.args.get('page', '1'))
    with_studies = bool(request.args.get('with-studies', ''))
    per_page     = 10

    if with_studies:
        results, has_more = StudyMetabolite.search_by_name(g.db_session, term, page, per_page)
    else:
        results, has_more = Metabolite.search_by_name(g.db_session, term, page, per_page)

    return json.dumps({
        'results': results,
        'pagination': {'more': has_more},
    })
