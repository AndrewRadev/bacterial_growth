"""
Search for studies based on name, used metabolites, microbial strains, and
other criteria.
"""
import re

from flask import (
    g,
    render_template,
    request,
)
import sqlalchemy as sql

from app.view.forms.search_form import SearchForm, SearchFormClause
from app.model.lib.search_queries import dynamical_query
from app.model.orm import (
    Study,
    StudyUser,
)
from app.model.lib.study_search import StudySearch
from app.model.lib.util import is_ajax

_PER_PAGE = 5


def search_index_page():
    search = StudySearch(
        g.db_session,
        user=g.current_user,
        query=request.args.get('q'),
        ncbiIds=request.args.getlist('ncbiIds'),
        chebiIds=request.args.getlist('chebiIds'),
        per_page=_PER_PAGE,
        offset=int(request.args.get('offset', '0')),
    )

    studies = search.fetch_results()

    render_params = dict(
        search=search,
        studies=studies,
        offset=0,
    )

    if is_ajax(request):
        return render_template("pages/search/_index_update.html", **render_params)
    else:
        return render_template("pages/search/index.html", **render_params)


def advanced_search_index_page():
    form = SearchForm(request.args)

    template_clause = SearchFormClause()
    results = []

    if g.current_user and g.current_user.isAdmin:
        # Noop, show everything
        publish_clause = Study.publicId.isnot(None)
    elif g.current_user:
        publish_clause = sql.or_(
            Study.isPublished,
            StudyUser.userUniqueID == g.current_user.uuid
        )
    else:
        publish_clause = Study.isPublished

    if form.data['clauses'] and form.data['clauses'][0]['value']:
        if not form.data['clauses'][0]['option']:
            form.data

        query, values = dynamical_query(form.data['clauses'])
        value_dict = {f"value_{i}": v for i, v in enumerate(values)}
        studyIds = [
            studyId for (studyId,)
            in g.db_conn.execute(sql.text(query), value_dict)
        ]
    else:
        # TODO (2025-04-15) Extract, test with multiple users
        studyIds = g.db_session.scalars(
            sql.select(Study.publicId)
            .join(StudyUser, isouter=True)
            .where(publish_clause)
            .group_by(Study)
            .limit(_PER_PAGE)
        ).all()

    if studyIds:
        results = g.db_session.scalars(
            sql.select(Study)
            .distinct()
            .where(Study.publicId.in_(studyIds))
            .where(publish_clause)
            .order_by(Study.createdAt.desc())
        ).all()

    return render_template(
        "pages/search/advanced.html",
        form=form,
        template_clause=template_clause,
        results=results,
    )
