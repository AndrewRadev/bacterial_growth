from typing import List
from decimal import Decimal

import sqlalchemy as sql
from sqlalchemy.orm import (
    mapped_column,
    relationship,
    Mapped,
)

from app.model.orm.orm_base import OrmBase

PROPERTY_NAMES = {
    'volume':                'volume',
    'pressure':              'pressure',
    'stirringMode':          'stirring mode',
    'stirringSpeed':         'stirring speed',
    'O2':                    'O<sub>2</sub>',
    'CO2':                   'CO<sub>2</sub>',
    'H2':                    'H<sub>2</sub>',
    'N2':                    'N<sub>2</sub>',
    'inoculumConcentration': 'inoculum concentration',
    'inoculumVolume':        'inoculum volume',
    'initialPh':             'initial pH',
    'initialTemperature':    'initial temperature',
}

PROPERTY_UNITS = {
    'volume':                'mL',
    'pressure':              'atm',
    'stirringMode':          '',
    'stirringSpeed':         'rpm',
    'O2':                    '%',
    'CO2':                   '%',
    'H2':                    '%',
    'N2':                    '%',
    'inoculumConcentration': ' Cells/mL',
    'inoculumVolume':        'mL',
    'initialPh':             '',
    'initialTemperature':    '°C',
}


class Compartment(OrmBase):
    __tablename__ = "Compartments"

    id:   Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(sql.String(100), nullable=False)

    # Note: convert to studyUniqueID or delete
    studyId: Mapped[str] = mapped_column(sql.ForeignKey('Studies.publicId'), nullable=False)
    study: Mapped['Study'] = relationship(back_populates='compartments')

    volume:        Mapped[Decimal] = mapped_column(sql.Numeric(7, 2), nullable=True)
    pressure:      Mapped[Decimal] = mapped_column(sql.Numeric(7, 2), nullable=True)
    stirringSpeed: Mapped[Decimal] = mapped_column(sql.Numeric(7, 2), nullable=True)
    stirringMode:  Mapped[str]     = mapped_column(sql.String(50), nullable=True)

    O2:  Mapped[Decimal] = mapped_column(sql.Numeric(7, 2), nullable=True)
    CO2: Mapped[Decimal] = mapped_column(sql.Numeric(7, 2), nullable=True)
    H2:  Mapped[Decimal] = mapped_column(sql.Numeric(7, 2), nullable=True)
    N2:  Mapped[Decimal] = mapped_column(sql.Numeric(7, 2), nullable=True)

    inoculumConcentration: Mapped[Decimal] = mapped_column(sql.Numeric(20, 3), nullable=True)
    inoculumVolume:        Mapped[Decimal] = mapped_column(sql.Numeric(7, 2), nullable=True)
    initialPh:             Mapped[Decimal] = mapped_column(sql.Numeric(7, 2), nullable=True)
    initialTemperature:    Mapped[Decimal] = mapped_column(sql.Numeric(7, 2), nullable=True)

    mediumName: Mapped[str]  = mapped_column(sql.String(100), nullable=True)
    mediumUrl:  Mapped[str]  = mapped_column(sql.String(100), nullable=True)

    experimentCompartments: Mapped[List['ExperimentCompartment']] = relationship(back_populates='compartment')
    experiments: Mapped[List['Experiment']] = relationship(
        secondary="ExperimentCompartments",
        viewonly=True
    )

    measurementContexts: Mapped[List['MeasurementContext']] = relationship(back_populates='compartment')
    measurements: Mapped[List['Measurement']] = relationship(
        order_by='Measurement.timeInSeconds',
        secondary='MeasurementContexts',
        viewonly=True,
    )

    @property
    def properties_description(self):
        formatted_properties = []

        for prop, name in PROPERTY_NAMES.items():
            units = PROPERTY_UNITS[prop]
            value = getattr(self, prop)

            if value is None or value == '':
                continue

            formatted_properties.append(f"<strong>{value}{units}</strong> {name}")

        return ', '.join(formatted_properties)

    def diff(self, other):
        changes = []

        for prop in PROPERTY_NAMES.keys():
            value       = getattr(self, prop)
            other_value = getattr(other, prop)

            if value != other_value:
                changes.append((PROPERTY_NAMES[prop], value, other_value))

        return changes
