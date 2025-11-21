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
    TECHNIQUE_SUBJECT_NAMES,
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
        units = f" in {self.units}" if self.units else ""
        label = f" ({self.label})" if self.label else ""

        return f"{self.short_name}{label}{units}"

    @property
    def short_name_with_subject_type(self):
        result = self.short_name

        if self.subjectType != 'metabolite':
            result += f" per {TECHNIQUE_SUBJECT_NAMES[self.subjectType]}"

        return result

    @property
    def long_name(self):
        return TECHNIQUE_LONG_NAMES[self.type]

    @property
    def long_name_with_subject_type(self):
        result = self.long_name

        if self.subjectType != 'metabolite':
            result += f" per {TECHNIQUE_SUBJECT_NAMES[self.subjectType]}"

        if self.label and self.label != '':
            result += f" ({self.label})"

        return result
