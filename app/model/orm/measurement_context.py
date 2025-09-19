from typing import List

import sqlalchemy as sql
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from app.model.orm.orm_base import OrmBase
from app.model.lib.db import execute_into_df


class MeasurementContext(OrmBase):
    """
    A collection of measurements of a particular subject with a particular technique.

    All connections between measurements and other entities are encapsulated
    here, so the individual ``Measurement`` objects can be packages of time and
    value alone.
    """

    __tablename__ = "MeasurementContexts"

    id: Mapped[int] = mapped_column(primary_key=True)

    bioreplicateId: Mapped[int] = mapped_column(sql.ForeignKey('Bioreplicates.id'))
    bioreplicate: Mapped['Bioreplicate'] = relationship(back_populates='measurementContexts')

    compartmentId: Mapped[int] = mapped_column(sql.ForeignKey('Compartments.id'))
    compartment: Mapped['Compartment'] = relationship(back_populates='measurementContexts')

    studyId: Mapped[str] = mapped_column(sql.ForeignKey('Studies.publicId'), nullable=False)
    study: Mapped['Study'] = relationship(back_populates='measurementContexts')

    techniqueId: Mapped[int] = mapped_column(sql.ForeignKey("MeasurementTechniques.id"))
    technique: Mapped['MeasurementTechnique'] = relationship(
        back_populates='measurementContexts'
    )

    measurements: Mapped[List['Measurement']] = relationship(
        back_populates='context',
        cascade='all, delete-orphan',
    )
    modelingResults: Mapped[List['ModelingResult']] = relationship(
        back_populates='measurementContext',
        cascade='all, delete-orphan',
    )

    calculationType: Mapped[str] = mapped_column(sql.String(50))

    subjectId:   Mapped[int] = mapped_column(sql.Integer,     nullable=False)
    subjectType: Mapped[str] = mapped_column(sql.String(100), nullable=False)

    def get_df(self, db_session):
        from app.model.orm import Measurement

        query = (
            sql.select(
                Measurement.timeInHours.label("time"),
                Measurement.value,
                Measurement.std,
            )
            .join(MeasurementContext)
            .where(
                MeasurementContext.id == self.id,
                Measurement.value.is_not(None),
            )
            .order_by(Measurement.timeInSeconds)
        )

        return execute_into_df(db_session, query)

    def get_chart_label(self, db_session):
        subject      = self.get_subject(db_session)
        technique    = self.technique
        bioreplicate = self.bioreplicate
        compartment  = self.compartment
        experiment   = bioreplicate.experiment

        if technique.subjectType == 'metabolite':
            label_parts = [f"<b>{subject.name}</b>"]
        else:
            label_parts = [technique.short_name]

        if len(experiment.compartments) <= 1:
            bioreplicate_label = f"<b>{bioreplicate.name}</b>"
        else:
            bioreplicate_label = f"<b>{bioreplicate.name}<sub>{compartment.name}</sub></b>"

        if technique.subjectType == 'bioreplicate':
            label_parts.append('of the')
            label_parts.append(bioreplicate_label)
            label_parts.append('community')
        elif technique.subjectType == 'metabolite':
            label_parts.append('in')
            label_parts.append(bioreplicate_label)
        else:
            label_parts.append('of')
            label_parts.append(f"<b>{subject.name}</b>")
            label_parts.append('in')
            label_parts.append(bioreplicate_label)

        label = ' '.join(label_parts)

        return label

    def get_subject(self, db_session):
        if not hasattr(db_session, '_measurement_subject_cache'):
            setattr(db_session, '_measurement_subject_cache', {})

        cache_key = (self.subjectType, self.subjectId)
        if cache_key in db_session._measurement_subject_cache:
            return db_session._measurement_subject_cache[cache_key]

        from app.model.orm import Metabolite, Strain, Bioreplicate

        if self.subjectType == 'metabolite':
            SubjectClass = Metabolite
        elif self.subjectType == 'strain':
            SubjectClass = Strain
        elif self.subjectType == 'bioreplicate':
            SubjectClass = Bioreplicate
        else:
            raise ValueError(f"Unknown subject type: {self.subjectType}")

        subject = db_session.get(SubjectClass, self.subjectId)
        db_session._measurement_subject_cache[cache_key] = subject

        return db_session._measurement_subject_cache[cache_key]
