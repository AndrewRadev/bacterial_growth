from datetime import datetime

import sqlalchemy as sql
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
    validates,
)
from sqlalchemy_utc.sqltypes import UtcDateTime

from app.model.orm.orm_base import OrmBase


class CustomModel(OrmBase):
    """
    The description of a user-created model type.
    """

    __tablename__ = "CustomModels"

    id: Mapped[int] = mapped_column(primary_key=True)

    studyId: Mapped[int] = mapped_column(sql.ForeignKey('Studies.publicId'), nullable=False)
    study: Mapped['Study'] = relationship(back_populates='customModels')

    name:        Mapped[str] = mapped_column(sql.String(255), nullable=False)
    shortName:   Mapped[str] = mapped_column(sql.String(5))
    url:         Mapped[str] = mapped_column(sql.String(255))
    description: Mapped[str] = mapped_column(sql.String)

    coefficientNames: Mapped[sql.JSON] = mapped_column(sql.JSON, nullable=False)
    fitNames:         Mapped[sql.JSON] = mapped_column(sql.JSON, nullable=False)

    createdAt: Mapped[datetime] = mapped_column(UtcDateTime, server_default=sql.FetchedValue())
    updatedAt: Mapped[datetime] = mapped_column(UtcDateTime, server_default=sql.FetchedValue())
