from datetime import datetime
from typing import List

import sqlalchemy as sql
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
    column_property,
)
from sqlalchemy_utc.sqltypes import UtcDateTime

from app.model.orm.orm_base import OrmBase
from app.model.lib.techniques import (
    TECHNIQUE_SHORT_NAMES,
    TECHNIQUE_LONG_NAMES,
)


class StudyTechnique(OrmBase):
    "A technique used within a study, parent to one or more MeasurementTechnique records"

    __tablename__ = "StudyTechniques"

    id: Mapped[int] = mapped_column(primary_key=True)

    type:        Mapped[str] = mapped_column(sql.String(100), nullable=False)
    subjectType: Mapped[str] = mapped_column(sql.String(100), nullable=False)
    units:       Mapped[str] = mapped_column(sql.String(100), nullable=False)
    includeStd:  Mapped[bool] = mapped_column(sql.Boolean, nullable=False, default=False)

    label:       Mapped[str] = mapped_column(sql.String(100))
    description: Mapped[str] = mapped_column(sql.String)

    studyId: Mapped[str] = mapped_column(sql.ForeignKey('Studies.publicId'), nullable=False)
    study: Mapped['Study'] = relationship(back_populates="studyTechniques")

    createdAt: Mapped[datetime] = mapped_column(UtcDateTime, server_default=sql.FetchedValue())
    updatedAt: Mapped[datetime] = mapped_column(UtcDateTime, server_default=sql.FetchedValue())

    measurementTechniques: Mapped[List['MeasurementTechnique']] = relationship(
        back_populates="studyTechnique",
        cascade='all, delete-orphan',
    )

    # Order techniques based on their type, according to the way they're
    # defined in the name index: FC first, then OD, etc.
    typeOrdering = column_property(OrmBase.list_ordering(
        type,
        TECHNIQUE_SHORT_NAMES.keys(),
    ))

    # Order records based on their subject type
    subjectTypeOrdering = column_property(OrmBase.list_ordering(
        subjectType,
        ('bioreplicate', 'strain', 'metabolite'),
    ))

    @property
    def short_name(self):
        return TECHNIQUE_SHORT_NAMES[self.type]

    @property
    def short_name_with_units(self):
        units = f" ({self.units})" if self.units else ""

        return f"{TECHNIQUE_SHORT_NAMES[self.type]}{units}"

    @property
    def long_name(self):
        return TECHNIQUE_LONG_NAMES[self.type]

    @property
    def long_name_with_subject_type(self):
        result = self.long_name

        if self.subjectType != 'metabolite':
            result += f" per {self.subject_short_name}"

        if self.label and self.label != '':
            result += f" ({self.label})"

        return result

    @property
    def subject_short_name(self):
        match self.subjectType:
            case 'bioreplicate': return 'community'
            case 'strain': return 'strain'
            case 'metabolite': return 'metabolite'
