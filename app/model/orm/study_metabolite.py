import sqlalchemy as sql
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from app.model.orm.orm_base import OrmBase


class StudyMetabolite(OrmBase):
    "Join table between Studies and Metabolites"

    __tablename__ = 'StudyMetabolites'

    id: Mapped[int] = mapped_column(sql.Integer, primary_key=True, autoincrement=True)

    studyId: Mapped[str] = mapped_column(sql.ForeignKey('Studies.publicId'),    primary_key=True)
    chebiId: Mapped[str] = mapped_column(sql.ForeignKey('Metabolites.chebiId'), primary_key=True)

    study:      Mapped['Study']      = relationship(back_populates="studyMetabolites")
    metabolite: Mapped['Metabolite'] = relationship(back_populates="studyMetabolites")

    @staticmethod
    def search_by_name(db_session, term, page=1, per_page=10):
        from app.model.orm import Metabolite

        term   = term.lower().strip()
        limit  = per_page
        offset = (page - 1) * per_page

        if term:
            term_pattern = '%' + '%'.join(term.split()) + '%'
            first_word = term.split()[0]
        else:
            term_pattern = '%'
            first_word = ''

        results = db_session.execute(
            sql.select(
                StudyMetabolite.chebiId,
                Metabolite.name,
            )
            .distinct()
            .join(Metabolite)
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
            sql.select(sql.func.count(StudyMetabolite.chebiId.distinct()))
            .join(Metabolite)
            .where(sql.func.lower(Metabolite.name).like(term_pattern))
        ).one()
        has_more = (page * per_page < total_count)

        return results, has_more
