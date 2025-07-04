import re
from typing import List

import sqlalchemy as sql
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)
from sqlalchemy.ext.hybrid import hybrid_property

from app.model.orm.orm_base import OrmBase


class Project(OrmBase):
    __tablename__ = 'Projects'

    uuid:      Mapped[str] = mapped_column(sql.String(100), primary_key=True)
    ownerUuid: Mapped[str] = mapped_column(sql.ForeignKey('Users.uuid'))

    owner: Mapped['User'] = relationship(back_populates='ownedProjects')

    publicId:    Mapped[str] = mapped_column(sql.String(100), nullable=False)
    name:        Mapped[str] = mapped_column(sql.String(100), nullable=False)
    description: Mapped[str] = mapped_column(sql.String,      nullable=False)

    projectUsers: Mapped[List['ProjectUser']] = relationship(back_populates="project")
    studies:      Mapped[List['Study']]       = relationship(back_populates="project")

    @property
    def studyUuids(self):
        return [s.uuid for s in self.studies]

    @property
    def managerUuids(self):
        return {pu.userUniqueID for pu in self.projectUsers}

    @staticmethod
    def generate_public_id(db_session):
        last_string_id = db_session.scalars(
            sql.select(Project.publicId)
            .order_by(Project.publicId.desc())
            .limit(1)
        ).one_or_none()

        if last_string_id:
            last_numeric_id = int(re.sub(r'PMGDB0*', '', last_string_id))
        else:
            last_numeric_id = 0

        return "PMGDB{:06d}".format(last_numeric_id + 1)
