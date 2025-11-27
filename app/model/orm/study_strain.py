from typing import List

import sqlalchemy as sql
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)
from sqlalchemy.ext.hybrid import hybrid_property

from app.model.orm.orm_base import OrmBase


class StudyStrain(OrmBase):
    "A microbial strain used in a particular study"

    __tablename__ = 'StudyStrains'

    id: Mapped[int] = mapped_column(sql.Integer, primary_key=True)

    name:        Mapped[str]  = mapped_column(sql.String(100))
    description: Mapped[str]  = mapped_column(sql.String)

    defined: Mapped[bool] = mapped_column(sql.Boolean, nullable=False, default=True)
    ncbiId:  Mapped[int]  = mapped_column(sql.ForeignKey("Taxa.ncbiId"))

    studyId: Mapped[str] = mapped_column(sql.ForeignKey('Studies.publicId'), nullable=False)
    study: Mapped['Study'] = relationship(back_populates="strains")

    userUniqueID: Mapped[str] = mapped_column(sql.String(100))

    taxon: Mapped['Taxon'] = relationship(back_populates="studyStrains")

    communityStrains: Mapped[List['CommunityStrain']] = relationship(
        back_populates='strain',
        cascade='all, delete-orphan',
    )

    @staticmethod
    def search_by_name(db_session, term, page=1, per_page=10):
        from app.model.orm import Taxon

        term   = term.lower().strip()
        limit  = per_page
        offset = (page - 1) * per_page

        if term:
            term_pattern = '%'.join(term.split()) + '%'
            first_word = term.split()[0]
        else:
            term_pattern = '%'
            first_word = ''

        results = db_session.execute(
            sql.select(
                Taxon.ncbiId,
                Taxon.name,
            )
            .distinct()
            .join(StudyStrain)
            .where(sql.func.lower(Taxon.name).like(term_pattern))
            .order_by(
                sql.func.locate(first_word, sql.func.lower(Taxon.name)).asc(),
                sql.func.lower(Taxon.name).asc()
            )
            .limit(limit)
            .offset(offset)
        ).all()

        results = [{'id': row[0], 'text': f"{row[1]} (NCBI:{row[0]})"} for row in results]

        total_count = db_session.scalars(
            sql.select(sql.func.count(Taxon.ncbiId.distinct()))
            .join(StudyStrain)
            .where(sql.func.lower(Taxon.name).like(term_pattern))
        ).one()
        has_more = (page * per_page < total_count)

        return results, has_more

    def __lt__(self, other):
        return self.name < other.name

    @hybrid_property
    def isUnknown(self):
        return self.ncbiId == 0

    @hybrid_property
    def notUnknown(self):
        return self.ncbiId != 0

    @property
    def externalId(self):
        """
        For compatibility with other subjects of measurements.
        The strain's (or parent strain's) NCBI id, e.g. "NCBI:1234"
        """
        return f"NCBI:{self.ncbiId}"
