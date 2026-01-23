import json
from datetime import datetime

import sqlalchemy as sql
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)
from sqlalchemy_utc.sqltypes import UtcDateTime

from app.model.orm.orm_base import OrmBase


class PageVisitCounter(OrmBase):
    """
    A record of a single visit of a page in the app, intended to be aggregated
    into counts and deleted on a regular basis.
    """
    __tablename__ = 'PageVisitCounters'

    id: Mapped[int] = mapped_column(primary_key=True)
    counts: Mapped[sql.JSON] = mapped_column(sql.JSON, nullable=False)

    startTimestamp: Mapped[datetime] = mapped_column(UtcDateTime, server_default=sql.FetchedValue())
    endTimestamp:   Mapped[datetime] = mapped_column(UtcDateTime, server_default=sql.FetchedValue())
    createdAt:      Mapped[datetime] = mapped_column(UtcDateTime, server_default=sql.FetchedValue())
