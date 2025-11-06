from datetime import datetime
from typing import List

import sqlalchemy as sql
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)
from sqlalchemy_utc.sqltypes import UtcDateTime

from app.model.orm.orm_base import OrmBase

TECHNIQUE_LONG_NAMES = {
    'ph':         'pH',
    'fc':         'Flow Cytometry',
    'od':         'Optical Density',
    'plates':     'Plate Counts',
    '16s':        '16S-rRNA reads',
    'qpcr':       'qPCR',
    'metabolite': 'Metabolites',
}
"Human-readable long names of techniques"


class StudyTechnique(OrmBase):
    "A technique used within a study, parent to one or more MeasurementTechnique records"

    __tablename__ = "StudyTechniques"

    id: Mapped[int] = mapped_column(primary_key=True)

    type:  Mapped[str] = mapped_column(sql.String(100), nullable=False)
    subjectType: Mapped[str] = mapped_column(sql.String(100), nullable=False)

    description: Mapped[str]  = mapped_column(sql.String)

    studyId: Mapped[str] = mapped_column(sql.ForeignKey('Studies.publicId'), nullable=False)
    study: Mapped['Study'] = relationship(back_populates="studyTechniques")

    createdAt: Mapped[datetime] = mapped_column(UtcDateTime, server_default=sql.FetchedValue())
    updatedAt: Mapped[datetime] = mapped_column(UtcDateTime, server_default=sql.FetchedValue())

    measurementTechniques: Mapped[List['MeasurementTechnique']] = relationship(
        back_populates="studyTechnique",
    )

    @property
    def long_name(self):
        return TECHNIQUE_LONG_NAMES[self.type]

    @property
    def long_name_with_subject_type(self):
        parts = [self.long_name]

        if self.subjectType != 'metabolite':
            parts.append(self.subject_short_name)

        return ' per '.join(parts)

    @property
    def subject_short_name(self):
        match self.subjectType:
            case 'bioreplicate': return 'community'
            case 'strain': return 'strain'
            case 'metabolite': return 'metabolite'
