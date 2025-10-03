import csv
from io import StringIO
from decimal import Decimal

import sqlalchemy as sql
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)
from sqlalchemy.ext.hybrid import hybrid_property

from app.model.orm.orm_base import OrmBase
from app.model.lib.conversion import convert_time
from app.model.lib.util import group_by_unique_name, is_non_negative_float


class Measurement(OrmBase):
    """
    A single observed measurement at a particular time point.

    A measurement may be an average of multiple technical replicates with a
    standard deviation. It may also be a "calculated" measurement from an
    average of multiple biological replicates. This information is encapsulated
    in a ``MeasurementContext``, while this record mostly contains the time and
    recorded value.
    """

    __tablename__ = "Measurements"

    # A relationship that goes through the parent measurement context:
    context_relationship = lambda: relationship(
        secondary='MeasurementContexts',
        viewonly=True,
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    studyId: Mapped[str] = mapped_column(sql.ForeignKey('Studies.publicId'), nullable=False)
    study: Mapped['Study'] = relationship(back_populates='measurements')

    contextId: Mapped[int] = mapped_column(sql.ForeignKey('MeasurementContexts.id'))
    context: Mapped['MeasurementContext'] = relationship(back_populates='measurements')

    bioreplicate: Mapped['Bioreplicate']         = context_relationship()
    compartment:  Mapped['Compartment']          = context_relationship()
    technique:    Mapped['MeasurementTechnique'] = context_relationship()

    timeInSeconds: Mapped[int] = mapped_column(sql.Integer,     nullable=False)

    value: Mapped[Decimal] = mapped_column(sql.Numeric(20, 2), nullable=True)
    std:   Mapped[Decimal] = mapped_column(sql.Numeric(20, 2), nullable=True)

    @hybrid_property
    def timeInHours(self):
        return self.timeInSeconds / 3600

    @hybrid_property
    def subjectId(self):
        return self.context.subjectId

    @hybrid_property
    def subjectType(self):
        return self.context.subjectType

    @classmethod
    def insert_from_csv_string(Self, db_session, study, csv_string, subject_type):
        from app.model.orm import MeasurementContext

        reader = csv.DictReader(StringIO(csv_string), dialect='unix')

        bioreplicates_by_name = group_by_unique_name(study.bioreplicates)
        compartments_by_name  = group_by_unique_name(study.compartments)
        context_cache = {}

        measurements = []

        for row in reader:
            bioreplicate = bioreplicates_by_name[row['Biological Replicate'].strip()]
            compartment  = compartments_by_name[row['Compartment'].strip()]

            if bioreplicate is None or compartment is None:
                # Missing entry, skip
                continue

            if not is_non_negative_float(row['Time'], isnan_check=True):
                # Missing time, skip
                continue

            time_in_seconds = convert_time(row['Time'], source=study.timeUnits, target='s')

            for technique in study.measurementTechniques:
                if technique.subjectType != subject_type:
                    continue

                if subject_type == 'bioreplicate':
                    subjects = [bioreplicate]
                elif subject_type == 'strain':
                    subjects = study.strains
                elif subject_type == 'metabolite':
                    subjects = study.metabolites
                else:
                    raise KeyError(f"Unexpected subject type: {subject_type}")

                for subject in subjects:
                    value_column_name = technique.csv_column_name(subject.name)

                    value = row[value_column_name]
                    if value == '':
                        value = None

                    std = row.get(f"{value_column_name} STD", None)
                    if std == '':
                        std = None

                    # Create a measurement context only if it doesn't already exist:
                    context_key = (bioreplicate.id, compartment.id, technique.id, subject.id, subject_type)
                    if context_key not in context_cache:
                        context = MeasurementContext(
                            # Relationships:
                            study=study,
                            bioreplicate=bioreplicate,
                            compartment=compartment,
                            # Subject:
                            subjectId=subject.id,
                            subjectType=subject_type,
                            # Technique:
                            techniqueId=technique.id,
                        )
                        context_cache[context_key] = context

                    context = context_cache[context_key]
                    measurement = Measurement(
                        study=study,
                        context=context,
                        timeInSeconds=time_in_seconds,
                        value=value,
                        std=std,
                    )
                    measurements.append(measurement)

        db_session.add_all(measurements)
        db_session.commit()

        # Prune measurement contexts that only have empty values:
        measurements = []

        for _, context in context_cache.items():
            if all([m.value is None for m in context.measurements]):
                db_session.execute(
                    sql.delete(MeasurementContext)
                    .where(MeasurementContext.id == context.id)
                )
            else:
                measurements.extend(context.measurements)

        return measurements
