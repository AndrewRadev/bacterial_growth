from datetime import datetime

import sqlalchemy as sql
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)
from sqlalchemy_utc.sqltypes import UtcDateTime

from app.model.orm.orm_base import OrmBase


class SubmissionBackup(OrmBase):
    __tablename__ = 'SubmissionBackups'

    id: Mapped[int] = mapped_column(primary_key=True)

    projectId:   Mapped[int]      = mapped_column(sql.String,  nullable=False)
    studyId:     Mapped[int]      = mapped_column(sql.String,  nullable=False)
    userUuid:    Mapped[str]      = mapped_column(sql.String,  nullable=False)
    dataFileId:  Mapped[int]      = mapped_column(sql.Integer, nullable=False)
    studyDesign: Mapped[sql.JSON] = mapped_column(sql.JSON,    nullable=False)
    createdAt:   Mapped[datetime] = mapped_column(UtcDateTime, server_default=sql.FetchedValue())
