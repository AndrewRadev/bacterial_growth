from datetime import datetime
from typing import List
import itertools

import sqlalchemy as sql
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)
from sqlalchemy_utc.sqltypes import UtcDateTime

from app.model.orm.orm_base import OrmBase

TECHNIQUE_SHORT_NAMES = {
    'ph':         'pH',
    'fc':         'FC',
    'od':         'OD',
    'plates':     'PC',
    '16s':        '16S-rRNA reads',
    'qpcr':       'qPCR',
    'metabolite': 'Metabolite',
}
"Human-readable short names of techniques"

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


class MeasurementTechnique(OrmBase):
    "The technique used for a particular set of measurements."

    __tablename__ = "MeasurementTechniques"

    id: Mapped[int] = mapped_column(primary_key=True)

    type:     Mapped[str] = mapped_column(sql.String(100), nullable=False)
    cellType: Mapped[str] = mapped_column(sql.String(100), nullable=True)
    subjectType: Mapped[str] = mapped_column(sql.String(100), nullable=False)

    # TODO (2025-11-10) Remove
    units:    Mapped[str] = mapped_column(sql.String(100), nullable=False)

    # TODO (2025-11-10) Remove
    description: Mapped[str]  = mapped_column(sql.String)

    metaboliteIds: Mapped[sql.JSON] = mapped_column(sql.JSON, nullable=False)

    # TODO (2025-11-10) Remove
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
        order_by='MeasurementContext.calculationType.is_(None), MeasurementContext.bioreplicateId, MeasurementContext.compartmentId',
    )
    measurements: Mapped[List['Measurement']] = relationship(
        secondary='MeasurementContexts',
        viewonly=True,
    )

    def __lt__(self, other):
        return self.id < other.id

    @property
    def short_name(self):
        cell_type = f" {self.cellType}" if self.cellType else ""
        return f"{TECHNIQUE_SHORT_NAMES[self.type]}{cell_type}"

    @property
    def short_name_with_units(self):
        units = f" ({self.units})" if self.units else ""
        return f"{self.short_name}{units}"

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
        cell_type = f"{self.cellType} " if self.cellType else ""

        if self.subjectType == 'bioreplicate':
            return f"Community {cell_type}{TECHNIQUE_SHORT_NAMES[self.type]}"

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

            return f"{subject_name} {cell_type}{suffix}"

    def get_grouped_contexts(self):
        grouper = lambda mc: (mc.bioreplicate, mc.compartment)

        for ((bioreplicate, compartment), group) in itertools.groupby(self.measurementContexts, grouper):
            contexts = list(group)

            yield ((bioreplicate, compartment), contexts)

    def __str__(self):
        return f"<MeasurementTechnique type={self.type}, id={self.id}>"
