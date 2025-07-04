from typing import List

import sqlalchemy as sql
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from app.model.lib.db import execute_text
from app.model.orm.orm_base import OrmBase


class Strain(OrmBase):
    __tablename__ = 'Strains'

    id: Mapped[int] = mapped_column(sql.Integer, primary_key=True)

    name:        Mapped[str]  = mapped_column(sql.String(100))
    description: Mapped[str]  = mapped_column(sql.String)

    defined: Mapped[bool] = mapped_column(sql.Boolean, nullable=False, default=True)
    NCBId:   Mapped[int]  = mapped_column(sql.Integer)

    studyId: Mapped[str] = mapped_column(sql.ForeignKey('Studies.publicId'), nullable=False)
    study: Mapped['Study'] = relationship(back_populates="strains")

    userUniqueID: Mapped[str] = mapped_column(sql.String(100))

    communityStrains: Mapped[List['CommunityStrain']] = relationship(
        back_populates='strain',
        cascade='all, delete-orphan',
    )

    def __lt__(self, other):
        return self.name < other.name
