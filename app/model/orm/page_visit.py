from datetime import datetime
from urllib.parse import parse_qs

import sqlalchemy as sql
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)
from sqlalchemy_utc.sqltypes import UtcDateTime

from app.model.orm.orm_base import OrmBase


class PageVisit(OrmBase):
    """
    A record of a single visit of a page in the app, intended to be aggregated
    into counts and deleted on a regular basis.
    """
    __tablename__ = 'PageVisits'

    id: Mapped[int] = mapped_column(primary_key=True)

    path:      Mapped[str] = mapped_column(sql.String(255))
    query:     Mapped[str] = mapped_column(sql.String(255))
    referrer:  Mapped[str] = mapped_column(sql.String(255))
    ip:        Mapped[str] = mapped_column(sql.String(100))
    country:   Mapped[str] = mapped_column(sql.String(255))
    userAgent: Mapped[str] = mapped_column(sql.String)
    uuid:      Mapped[str] = mapped_column(sql.String(36))

    isUser:  Mapped[bool] = mapped_column(sql.Boolean, default=False)
    isAdmin: Mapped[bool] = mapped_column(sql.Boolean, default=False)
    isBot:   Mapped[bool] = mapped_column(sql.Boolean, default=False)

    createdAt: Mapped[datetime] = mapped_column(UtcDateTime, server_default=sql.FetchedValue())

    @property
    def parsedQuery(self):
        if self.query is None:
            return None

        return parse_qs(self.query)
