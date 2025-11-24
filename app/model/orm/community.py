from typing import List

import sqlalchemy as sql
from sqlalchemy.orm import (
    mapped_column,
    relationship,
    Mapped,
)

from app.model.orm.orm_base import OrmBase


class Community(OrmBase):
    "A collection of strains measured in a particular study"

    __tablename__ = "Communities"

    id:   Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(sql.String(100), nullable=False)

    # Note: convert to studyUniqueID or delete
    studyId: Mapped[str] = mapped_column(sql.ForeignKey('Studies.publicId'), nullable=False)
    study: Mapped['Study'] = relationship(back_populates='communities')

    experiments: Mapped[List['Experiment']] = relationship(back_populates='community')

    communityStrains: Mapped[List['CommunityStrain']] = relationship(
        back_populates='community',
        cascade='all, delete-orphan',
    )
    strains: Mapped[List['StudyStrain']] = relationship(
        secondary='CommunityStrains',
        viewonly=True,
    )

    def diff(self, other):
        strains       = frozenset(self.strains)
        other_strains = frozenset(other.strains)

        return {
            'added':   other_strains - strains,
            'removed': strains - other_strains,
        }
