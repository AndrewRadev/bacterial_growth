import sqlalchemy as sql

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)

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
    userAgent: Mapped[str] = mapped_column(sql.String)

    isUser:  Mapped[bool] = mapped_column(sql.Boolean, default=False)
    isAdmin: Mapped[bool] = mapped_column(sql.Boolean, default=False)
