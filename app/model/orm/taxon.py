import re

import sqlalchemy as sql
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
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

    @property
    def short_name(self):
        return re.sub(r'^([A-Z])[A-Za-z]+ ', r'\1. ', self.name)

    @staticmethod
    def search_by_name(db_conn, term, page=1, per_page=10):
        term = term.lower().strip()
        if len(term) <= 0:
            return [], 0

        term_pattern = '%'.join(term.split()) + '%'

        query = """
            SELECT
                ncbiId,
                CONCAT(name, ' (NCBI:', ncbiId, ')') AS text
            FROM Taxa
            WHERE LOWER(name) LIKE :term_pattern
            ORDER BY LOWER(name) ASC
            LIMIT :per_page
            OFFSET :offset
        """
        results = db_conn.execute(sql.text(query), {
            'term_pattern': term_pattern,
            'per_page': per_page,
            'offset': (page - 1) * per_page,
        }).all()
        results = [{'id': row[0], 'text': row[1]} for row in results]

        count_query = """
            SELECT COUNT(*)
            FROM Taxa
            WHERE LOWER(name) LIKE :term_pattern
        """
        total_count = db_conn.execute(sql.text(count_query), {'term_pattern': term_pattern}).scalar()
        has_more = (page * per_page < total_count)

        return results, has_more
