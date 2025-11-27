import re

import sqlalchemy as sql

from app.model.orm import (
    Metabolite,
    Study,
    StudyMetabolite,
    StudyStrain,
    StudyUser,
    Taxon,
)


class StudySearch():
    def __init__(
        self,
        db_session,
        user=None,
        query=None,
        ncbiIds=None,
        chebiIds=None,
        per_page=10,
    ):
        self.db_session = db_session
        self.user       = user
        self.query      = (query or '').strip().lower()
        self.per_page   = per_page
        self.ncbiIds    = [int(n) for n in (ncbiIds or [])]
        self.chebiIds   = chebiIds or []

        self.query_words = []

    def fetch_results(self):
        publish_clause = self._build_publish_clause()

        db_query = (
            sql.select(Study)
            .distinct()
            .join(StudyUser, isouter=True)
            .where(publish_clause)
            .order_by(Study.publicId.desc())
            .limit(self.per_page)
        )

        if len(self.query):
            query = _replace_public_id_references(self.query)
            self.query_words = query.split()

            like_expr = '%' + '%'.join(self.query_words) + '%'

            db_query = db_query.where(
                sql.or_(
                    Study.name.ilike(like_expr),
                    Study.description.ilike(like_expr),
                    Study.publicId.in_(self.query_words),
                )
            )
        else:
            self.query_words = []

        if self.ncbiIds:
            db_query = db_query.join(StudyStrain).where(StudyStrain.ncbiId.in_(self.ncbiIds))

        if self.chebiIds:
            db_query = db_query.join(StudyMetabolite).where(StudyMetabolite.chebiId.in_(self.chebiIds))

        return self.db_session.scalars(db_query).all()

    def fetch_taxa(self):
        return self.db_session.scalars(
            sql.select(Taxon)
            .where(Taxon.ncbiId.in_(self.ncbiIds))
        ).all()

    def fetch_metabolites(self):
        return self.db_session.scalars(
            sql.select(Metabolite)
            .where(Metabolite.chebiId.in_(self.chebiIds))
        ).all()

    def _build_publish_clause(self):
        if self.user and self.user.isAdmin:
            # Noop, show everything
            return Study.publicId.isnot(None)
        elif self.user:
            return sql.or_(
                Study.isPublished,
                Study.ownerUuid == self.user.uuid,
                StudyUser.userUniqueID == self.user.uuid,
            )
        else:
            return Study.isPublished


def _replace_public_id_references(text):
    text = re.sub(r'\bSMGDB0*(\d+)', _replace_study_reference,      text, flags=re.IGNORECASE)
    # text = re.sub(r'\bPMGDB0*(\d+)', _replace_project_reference,    text, flags=re.IGNORECASE)
    # text = re.sub(r'\bEMGDB0*(\d+)', _replace_experiment_reference, text, flags=re.IGNORECASE)

    return text


def _replace_study_reference(m):
    return f"SMGDB{int(m[1]):08d}"


# def _replace_project_reference(m):
#     return f"PMGDB{int(m[1]):06d}"


# def _replace_experiment_reference(m):
#     return f"EMGDB{int(m[1]):09d}"
