import re
from typing import List
from datetime import datetime, UTC

import sqlalchemy as sql
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy_utc.sqltypes import UtcDateTime

from app.model.orm.orm_base import OrmBase


class Study(OrmBase):
    """
    The main container for a particular scientific study.

    Updates to experiments and measurements can only be done by issuing a
    ``Submission`` to update a particular study. Access control over the
    individual experiments is also done at the study level.

    It has a fixed ``publicId`` identifier starting with the prefix "SMGDB".
    """

    __tablename__ = 'Studies'

    # A relationship representing ownership of these records. Clearing them out
    # should directly delete them so they can be replaced.
    owner_relationship = lambda **kwargs: relationship(
        back_populates='study',
        cascade='all, delete-orphan',
        **kwargs
    )

    publicId: Mapped[str] = mapped_column(sql.String(100), primary_key=True)
    uuid:     Mapped[str] = mapped_column(sql.String(100), nullable=False)

    ownerUuid: Mapped[str]    = mapped_column(sql.ForeignKey('Users.uuid'))
    owner:     Mapped['User'] = relationship(back_populates='ownedStudies')

    name:        Mapped[str] = mapped_column(sql.String(255))
    description: Mapped[str] = mapped_column(sql.String, nullable=True)
    url:         Mapped[str] = mapped_column(sql.String, nullable=True)
    timeUnits:   Mapped[str] = mapped_column(sql.String(100))

    projectUuid: Mapped[str] = mapped_column(sql.ForeignKey('Projects.uuid'))
    project: Mapped['Project'] = relationship(back_populates="studies")

    createdAt:        Mapped[datetime] = mapped_column(UtcDateTime, server_default=sql.FetchedValue())
    updatedAt:        Mapped[datetime] = mapped_column(UtcDateTime, server_default=sql.FetchedValue())
    publishableAt:    Mapped[datetime] = mapped_column(UtcDateTime, nullable=True)
    publishedAt:      Mapped[datetime] = mapped_column(UtcDateTime, nullable=True)
    embargoExpiresAt: Mapped[datetime] = mapped_column(UtcDateTime, nullable=True)

    studyUsers:  Mapped[List['StudyUser']]  = owner_relationship()
    experiments: Mapped[List['Experiment']] = owner_relationship()
    strains:     Mapped[List['Strain']]     = owner_relationship(order_by='Strain.name')

    communities:  Mapped[List['Community']]   = owner_relationship()
    compartments: Mapped[List['Compartment']] = owner_relationship()

    studyTechniques:       Mapped[List['StudyTechnique']]       = owner_relationship()
    measurementTechniques: Mapped[List['MeasurementTechnique']] = owner_relationship()
    measurementContexts:   Mapped[List['MeasurementContext']]   = owner_relationship()
    modelingRequests:      Mapped[List['ModelingRequest']]      = owner_relationship()

    bioreplicates: Mapped[List['Bioreplicate']] = relationship(
        secondary='Experiments',
        viewonly=True,
    )

    measurements: Mapped[List['Measurement']] = relationship(
        order_by='Measurement.timeInSeconds',
        secondary='MeasurementContexts',
        viewonly=True,
    )

    modelingResults: Mapped[List['ModelingResult']] = relationship(
        secondary='ModelingRequests',
        viewonly=True,
    )

    studyMetabolites: Mapped[List['StudyMetabolite']] = owner_relationship()
    metabolites: Mapped[List['Metabolite']] = relationship(
        order_by='Metabolite.name',
        secondary='StudyMetabolites',
        viewonly=True,
    )

    @hybrid_property
    def isPublished(self):
        return self.publishedAt != None

    @property
    def isPublishable(self):
        now = datetime.now(UTC)

        if self.embargoExpiresAt:
            return self.embargoExpiresAt <= now
        elif self.publishableAt:
            return self.publishableAt <= now
        else:
            return False

    def visible_to_user(self, user):
        if self.isPublished:
            return True
        elif not user or not user.uuid:
            return False
        elif user.isAdmin:
            return True
        else:
            return user.uuid in self.managerUuids

    def manageable_by_user(self, user):
        if not user or not user.uuid:
            return False
        else:
            return user.uuid in self.managerUuids

    def find_last_submission(self, db_session):
        from app.model.orm import Submission

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
