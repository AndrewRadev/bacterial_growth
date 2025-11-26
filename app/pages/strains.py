import json

from flask import request, g

from db import get_connection
from app.model.orm import Taxon, StudyStrain


def taxa_completion_json():
    term         = request.args.get('term', '')
    page         = int(request.args.get('page', '1'))
    with_studies = bool(request.args.get('with-studies', ''))
    per_page     = 10

    if with_studies:
        results, has_more = StudyStrain.search_by_name(g.db_session, term, page, per_page)
    else:
        results, has_more = Taxon.search_by_name(g.db_session, term, page, per_page)

    return json.dumps({
        'results': results,
        'pagination': {'more': has_more},
    })
