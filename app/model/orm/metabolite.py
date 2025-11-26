from typing import List
from decimal import Decimal

import sqlalchemy as sql
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from app.model.orm.orm_base import OrmBase


class Metabolite(OrmBase):
    """
    A metabolite record imported from ChEBI.

    This entity is independent from any particular study and it represents the
    general information about a metabolite.
    """

    __tablename__ = 'Metabolites'

    id: Mapped[int] = mapped_column(primary_key=True)

    chebiId:    Mapped[str] = mapped_column(sql.String(100),  nullable=False)
    name:       Mapped[str] = mapped_column(sql.String(1024), nullable=False)
    definition: Mapped[str] = mapped_column(sql.String)

    averageMass: Mapped[Decimal] = mapped_column(sql.Numeric(10, 5))
    massIsEstimation: Mapped[bool] = mapped_column(sql.Boolean, default=False)

    studyMetabolites: Mapped[List['StudyMetabolite']] = relationship(
        back_populates="metabolite"
    )

    def __lt__(self, other):
        return self.name < other.name

    @property
    def externalId(self):
        """
        For compatibility with other subjects of measurements.
        The metabolite's ChEBI id, e.g. "CHEBI:1234"
        """
        return self.chebiId

    @staticmethod
    def search_by_name(db_session, term, page=1, per_page=10):
        term = term.lower().strip()
        if len(term) <= 0:
            return [], 0

        limit  = per_page
        offset = (page - 1) * per_page

        term_pattern = '%' + '%'.join(term.split()) + '%'
        first_word = term.split()[0]

        results = db_session.execute(
            sql.select(
                Metabolite.chebiId,
                Metabolite.name,
            )
            .where(sql.func.lower(Metabolite.name).like(term_pattern))
            .order_by(
                sql.func.locate(first_word, sql.func.lower(Metabolite.name)).asc(),
                sql.func.lower(Metabolite.name).asc()
            )
            .limit(limit)
            .offset(offset)
        ).all()

        results = [{'id': row[0], 'text': f"{row[1]} ({row[0]})"} for row in results]

        total_count = db_session.scalars(
            sql.select(sql.func.count(Metabolite.chebiId))
            .where(sql.func.lower(Metabolite.name).like(term_pattern))
        ).one()
        has_more = (page * per_page < total_count)

        return results, has_more
