import json

from flask import request, g, render_template, url_for
import sqlalchemy as sql

from db import get_connection
from app.model.orm import Metabolite, StudyMetabolite


def metabolite_show_page(chebiId):
    metabolite = g.db_session.scalars(
        sql.select(Metabolite)
        .where(Metabolite.chebiId == chebiId)
        .limit(1)
    ).one()

    study_count = g.db_session.scalars(
        sql.select(sql.func.count(StudyMetabolite.id))
        .where(StudyMetabolite.chebi_id == metabolite.chebiId)
    ).one()

    search_url = url_for(
        'search_index_page',
        **{
            'clauses-0-option': 'chEBI ID',
            'clauses-0-value': metabolite.chebiId,
        },
    )

    return render_template(
        'pages/metabolites/show.html',
        metabolite=metabolite,
        study_count=study_count,
        search_url=search_url,
    )


def metabolites_completion_json():
    term     = request.args.get('term', '')
    page     = int(request.args.get('page', '1'))
    per_page = 10

    with get_connection() as conn:
        results, has_more = Metabolite.search_by_name(conn, term, page, per_page)

        return json.dumps({
            'results': results,
            'pagination': {'more': has_more},
        })
