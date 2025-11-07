from datetime import datetime
from typing import List
import itertools

import sqlalchemy as sql
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
    column_property,
)
from sqlalchemy_utc.sqltypes import UtcDateTime

from app.model.orm.orm_base import OrmBase

TECHNIQUE_SHORT_NAMES = {
    'fc':         'FC',
    'od':         'OD',
    'plates':     'PC',
    '16s':        '16S-rRNA reads',
    'qpcr':       'qPCR',
    'ph':         'pH',
    'metabolite': 'Metabolite',
}
"Human-readable short names of techniques"

TECHNIQUE_LONG_NAMES = {
    'fc':         'Flow Cytometry',
    'od':         'Optical Density',
    'plates':     'Plate Counts',
    '16s':        '16S-rRNA reads',
    'qpcr':       'qPCR',
    'ph':         'pH',
    'metabolite': 'Metabolites',
}
"Human-readable long names of techniques"


class MeasurementTechnique(OrmBase):
    "The technique used for a particular set of measurements."

    __tablename__ = "MeasurementTechniques"

    id: Mapped[int] = mapped_column(primary_key=True)

    type:    Mapped[str] = mapped_column(sql.String(100), nullable=False)
    subtype: Mapped[str] = mapped_column(sql.String(100), nullable=True)
    units:   Mapped[str] = mapped_column(sql.String(100), nullable=False)

    subjectType: Mapped[str] = mapped_column(sql.String(100), nullable=False)

    description: Mapped[str]  = mapped_column(sql.String)
    includeStd:  Mapped[bool] = mapped_column(sql.Boolean, nullable=False, default=False)

    metaboliteIds: Mapped[sql.JSON] = mapped_column(sql.JSON, nullable=False)

    studyId: Mapped[str] = mapped_column(sql.ForeignKey('Studies.publicId'), nullable=False)
    study: Mapped['Study'] = relationship(back_populates="measurementTechniques")

    createdAt: Mapped[datetime] = mapped_column(UtcDateTime, server_default=sql.FetchedValue())
    updatedAt: Mapped[datetime] = mapped_column(UtcDateTime, server_default=sql.FetchedValue())

    studyTechniqueId: Mapped[int] = mapped_column(sql.ForeignKey('StudyTechniques.id'))
    studyTechnique: Mapped['StudyTechnique'] = relationship(
        back_populates="measurementTechniques"
    )

    measurementContexts: Mapped[List['MeasurementContext']] = relationship(
        back_populates="technique",
        order_by='MeasurementContext.calculationType.is_(None), MeasurementContext.bioreplicateId, MeasurementContext.compartmentId, MeasurementContext.subjectTypeOrdering, MeasurementContext.subjectName',
    )
    measurements: Mapped[List['Measurement']] = relationship(
        secondary='MeasurementContexts',
        viewonly=True,
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

    def __lt__(self, other):
        return self.id < other.id

    @property
    def short_name(self):
        return TECHNIQUE_SHORT_NAMES[self.type]

    @property
    def short_name_with_units(self):
        if self.units:
            units = f" ({self.units})"
        else:
            units = ""
        return f"{TECHNIQUE_SHORT_NAMES[self.type]}{units}"

    @property
    def short_name_with_subject_type(self):
        parts = [self.short_name]

        if self.subjectType != 'metabolite':
            parts.append(self.subject_short_name)

        return ' per '.join(parts)

    @property
    def long_name(self):
        return TECHNIQUE_LONG_NAMES[self.type]

    # TODO (2025-11-04) Can be removed in favor of using label
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

    @property
    def is_growth(self):
        return self.type not in ('ph', 'metabolite')

    def get_bioreplicates(self, db_session):
        from app.model.orm import Bioreplicate, MeasurementContext

        return db_session.scalars(
            sql.select(Bioreplicate)
            .distinct()
            .join(MeasurementContext)
            .where(MeasurementContext.techniqueId == self.id)
        ).all()

    def csv_column_name(self, subject_name=None):
        if self.subjectType == 'bioreplicate':
            return f"Community {TECHNIQUE_SHORT_NAMES[self.type]}"

        elif self.subjectType == 'metabolite':
            return subject_name

        elif self.subjectType == 'strain':
            if self.type == '16s':
                suffix = 'rRNA reads'
            elif self.type == 'qpcr':
                suffix = 'qPCR counts'
            elif self.type == 'fc':
                suffix = 'FC counts'
            elif self.type == 'plates':
                suffix = 'plate counts'
            else:
                raise ValueError(f"Incompatible type and subjectType: {self.type}, {self.subjectType}")

            return f"{subject_name} {suffix}"

    def get_grouped_contexts(self):
        grouper = lambda mc: (mc.bioreplicate, mc.compartment)

        for ((bioreplicate, compartment), group) in itertools.groupby(self.measurementContexts, grouper):
            contexts = list(group)

            yield ((bioreplicate, compartment), contexts)

    def __str__(self):
        return f"<MeasurementTechnique type={self.type}, id={self.id}>"
