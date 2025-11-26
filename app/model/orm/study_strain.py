from typing import List

import sqlalchemy as sql
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)
from sqlalchemy.ext.hybrid import hybrid_property

from app.model.orm.orm_base import OrmBase


class StudyStrain(OrmBase):
    "A microbial strain used in a particular study"

    __tablename__ = 'StudyStrains'

    id: Mapped[int] = mapped_column(sql.Integer, primary_key=True)

    name:        Mapped[str]  = mapped_column(sql.String(100))
    description: Mapped[str]  = mapped_column(sql.String)

    defined: Mapped[bool] = mapped_column(sql.Boolean, nullable=False, default=True)
    ncbiId:  Mapped[int]  = mapped_column(sql.Integer)

    studyId: Mapped[str] = mapped_column(sql.ForeignKey('Studies.publicId'), nullable=False)
    study: Mapped['Study'] = relationship(back_populates="strains")

    userUniqueID: Mapped[str] = mapped_column(sql.String(100))

    communityStrains: Mapped[List['CommunityStrain']] = relationship(
        back_populates='strain',
        cascade='all, delete-orphan',
    )

    def __lt__(self, other):
        return self.name < other.name

    @hybrid_property
    def isUnknown(self):
        return self.ncbiId == 0

    @hybrid_property
    def notUnknown(self):
        return self.ncbiId != 0

    @property
    def externalId(self):
        """
        For compatibility with other subjects of measurements.
        The strain's (or parent strain's) NCBI id, e.g. "NCBI:1234"
        """
        return f"NCBI:{self.ncbiId}"
