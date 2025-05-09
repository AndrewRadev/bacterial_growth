import re
from typing import List
from datetime import datetime, UTC

import sqlalchemy as sql
from sqlalchemy import (
    String,
    ForeignKey,
    FetchedValue,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy_utc.sqltypes import UtcDateTime

from models.orm_base import OrmBase


class Study(OrmBase):
    __tablename__ = 'Study'

    studyUniqueID: Mapped[str] = mapped_column(String(100), primary_key=True)

    studyId:          Mapped[str] = mapped_column(String(100))
    studyName:        Mapped[str] = mapped_column(String(100))
    studyDescription: Mapped[str] = mapped_column(String, nullable=True)
    studyURL:         Mapped[str] = mapped_column(String, nullable=True)
    timeUnits:        Mapped[str] = mapped_column(String(100))

    projectUniqueID: Mapped[str] = mapped_column(ForeignKey('Project.projectUniqueID'))

    project: Mapped['Project'] = relationship(back_populates="studies")

    studyUsers:  Mapped[List['StudyUser']]  = relationship(back_populates="study")
    experiments: Mapped[List['Experiment']] = relationship(back_populates='study')
    strains:     Mapped[List['Strain']]     = relationship(back_populates='study')

    measurementTechniques: Mapped[List['MeasurementTechnique']] = relationship(
        back_populates="study"
    )
    measurements: Mapped[List['Measurement']] = relationship(
        back_populates="study"
    )
    calculationTechniques: Mapped[List['CalculationTechnique']] = relationship(
        back_populates="study"
    )
    studyMetabolites: Mapped[List['StudyMetabolite']] = relationship(
        back_populates="study"
    )

    createdAt:        Mapped[datetime] = mapped_column(UtcDateTime, server_default=FetchedValue())
    updatedAt:        Mapped[datetime] = mapped_column(UtcDateTime, server_default=FetchedValue())
    publishableAt:    Mapped[datetime] = mapped_column(UtcDateTime, nullable=True)
    publishedAt:      Mapped[datetime] = mapped_column(UtcDateTime, nullable=True)
    embargoExpiresAt: Mapped[datetime] = mapped_column(UtcDateTime, nullable=True)

    @hybrid_property
    def uuid(self):
        return self.studyUniqueID

    @hybrid_property
    def publicId(self):
        return self.studyId

    @hybrid_property
    def name(self):
        return self.studyName

    @hybrid_property
    def isPublished(self):
        return self.publishedAt

    @hybrid_property
    def isPublishable(self):
        return self.publishableAt and self.publishableAt <= datetime.now(UTC)

    def visible_to_user(self, user):
        if self.isPublished:
            return True
        elif not user or not user.uuid:
            return False
        else:
            return user.uuid in self.managerUuids

    def manageable_by_user(self, user):
        if not user or not user.uuid:
            return False
        else:
            return user.uuid in self.managerUuids

    def find_last_submission(self, db_session):
        from models import Submission

        return db_session.scalars(
            sql.select(Submission)
            .where(Submission.studyUniqueID == self.uuid)
            .order_by(Submission.updatedAt.desc())
            .limit(1)
        ).one_or_none()

    @property
    def managerUuids(self):
        return {su.userUniqueID for su in self.studyUsers}

    def publish(self):
        if not self.isPublishable:
            return False
        else:
            self.publishedAt = datetime.now(UTC)
            return True

    @staticmethod
    def generate_public_id(db_session):
        last_string_id = db_session.scalars(
            sql.select(Study.publicId)
            .order_by(Study.publicId.desc())
            .limit(1)
        ).one_or_none()

        if last_string_id:
            last_numeric_id = int(re.sub(r'SMGDB0*', '', last_string_id))
        else:
            last_numeric_id = 0

        return "SMGDB{:08d}".format(last_numeric_id + 1)
