import re
from typing import List

import sqlalchemy as sql
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from app.model.orm.orm_base import OrmBase


class Taxon(OrmBase):
    """
    A taxon record imported from NCBI.

    This entity is independent from any particular study and it represents the
    general information about a specific taxon.
    """

    __tablename__ = 'Taxa'

    id: Mapped[int] = mapped_column(primary_key=True)

    ncbiId: Mapped[int] = mapped_column(sql.Integer)
    name:   Mapped[str] = mapped_column(sql.String(512))

    studyStrains: Mapped[List['StudyStrain']] = relationship(
        back_populates="taxon"
    )

    @property
    def short_name(self):
        return re.sub(r'^([A-Z])[A-Za-z]+ ', r'\1. ', self.name)

    @staticmethod
    def search_by_name(db_session, term, page=1, per_page=10):
        term = term.lower().strip()
        if len(term) <= 0:
            return [], 0

        limit  = per_page
        offset = (page - 1) * per_page

        term_pattern = '%'.join(term.split()) + '%'

        results = db_session.execute(
            sql.select(
                Taxon.ncbiId,
                Taxon.name,
            )
            .distinct()
            .where(sql.func.lower(Taxon.name).like(term_pattern))
            .order_by(sql.func.lower(Taxon.name).asc())
            .limit(limit)
            .offset(offset)
        ).all()

        results = [{'id': row[0], 'text': f"{row[1]} (NCBI:{row[0]})"} for row in results]

        total_count = db_session.scalars(
            sql.select(sql.func.count(Taxon.ncbiId.distinct()))
            .where(sql.func.lower(Taxon.name).like(term_pattern))
        ).one()

        has_more = (page * per_page < total_count)

        return results, has_more
