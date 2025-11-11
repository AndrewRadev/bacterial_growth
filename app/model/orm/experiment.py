import re
from typing import List

import sqlalchemy as sql
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from app.model.lib.db import execute_into_df
from app.model.orm.orm_base import OrmBase


class Experiment(OrmBase):
    """
    An entity that describes the design of a particular experiment.

    The specific measurements of an experiment are connected to its biological
    replicates (``Bioreplicate``), which are the concrete implementations of
    the experimental design.

    A published study contains experiments with fixed ``publicId`` identifiers
    starting with the prefix "EMGDB".
    """

    __tablename__ = "Experiments"

    publicId: Mapped[str] = mapped_column(sql.String(100), primary_key=True)

    name:        Mapped[str] = mapped_column(sql.String(100), nullable=False)
    description: Mapped[str] = mapped_column(sql.String)

    bioreplicates: Mapped[List['Bioreplicate']] = relationship(
        order_by='Bioreplicate.calculationType.is_(None), Bioreplicate.id',
        back_populates='experiment',
        cascade="all, delete-orphan"
    )

    communityId: Mapped[int] = mapped_column(sql.ForeignKey('Communities.id'))
    community: Mapped['Community'] = relationship(back_populates='experiments')

    studyId: Mapped[str] = mapped_column(sql.ForeignKey('Studies.publicId'), nullable=False)
    study: Mapped['Study'] = relationship(back_populates='experiments')

    cultivationMode: Mapped[str] = mapped_column(sql.String(50))

    experimentCompartments: Mapped[List['ExperimentCompartment']] = relationship(
        back_populates='experiment',
        cascade='all, delete-orphan'
    )
    compartments: Mapped[List['Compartment']] = relationship(
        secondary='ExperimentCompartments',
        viewonly=True,
    )

    perturbations: Mapped[List['Perturbation']] = relationship(
        back_populates='experiment',
        cascade="all, delete-orphan"
    )

    measurementContexts: Mapped[List['MeasurementContext']] = relationship(
        order_by='MeasurementContext.subjectTypeOrdering, MeasurementContext.subjectName',
        secondary='Bioreplicates',
        viewonly=True,
    )

    def get_df(self, db_session):
        from app.model.orm import (
            Bioreplicate,
            Compartment,
            Measurement,
            MeasurementTechnique,
            MeasurementContext,
        )

        query = (
            sql.select(
                Bioreplicate.id.label("bioreplicateId"),
                Bioreplicate.name.label("bioreplicateName"),
                Compartment.name.label("compartmentName"),
                MeasurementTechnique.type.label("techniqueType"),
                MeasurementContext.id.label("measurementContextId"),
                MeasurementContext.subjectType.label("subjectType"),
                MeasurementContext.subjectName.label("subjectName"),
                MeasurementContext.subjectExternalId.label("subjectExternalId"),
                Measurement.timeInHours.label("time"),
                Measurement.value,
                Measurement.std,
            )
            .distinct()
            .select_from(Measurement)
            .join(MeasurementContext)
            .join(Compartment)
            .join(Bioreplicate)
            .join(Experiment)
            .where(
                Experiment.publicId == self.publicId,
                Measurement.value.is_not(None),
            )
            .order_by(
                Bioreplicate.id,
                Compartment.name,
                MeasurementTechnique.type,
                MeasurementContext.id,
                Measurement.timeInHours,
            )
        )

        return execute_into_df(db_session, query)

    @staticmethod
    def generate_public_id(db_session):
        last_string_id = db_session.scalars(
            sql.select(Experiment.publicId)
            .order_by(Experiment.publicId.desc())
            .limit(1)
        ).one_or_none()

        if last_string_id:
            last_numeric_id = int(re.sub(r'EMGDB0*', '', last_string_id))
        else:
            last_numeric_id = 0

        return "EMGDB{:09d}".format(last_numeric_id + 1)
