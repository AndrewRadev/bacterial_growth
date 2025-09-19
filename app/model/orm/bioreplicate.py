from typing import List

import sqlalchemy as sql
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from app.model.orm.orm_base import OrmBase


class Bioreplicate(OrmBase):
    """
    A specific physical implementation of a particular experiment.

    This would usually be a specific vessel or a connected combination of
    vessels (``Compartment`` records). All bioreplicates of one particular
    experiment have the same experimental design. All measurements are made
    within the context of a bioreplicate.
    """

    __tablename__ = 'Bioreplicates'

    id:   Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(sql.String(100), nullable=False)

    position:     Mapped[str] = mapped_column(sql.String(100))
    biosampleUrl: Mapped[str] = mapped_column(sql.String)

    isControl: Mapped[bool] = mapped_column(sql.Boolean, nullable=False, default=False)
    isBlank:   Mapped[bool] = mapped_column(sql.Boolean, nullable=False, default=False)

    # Only set if the bioreplicate was generated and not uploaded
    calculationType: Mapped[str] = mapped_column(sql.String(50))

    experimentId: Mapped[str] = mapped_column(sql.ForeignKey('Experiments.publicId'), nullable=False)
    experiment: Mapped['Experiment'] = relationship(back_populates='bioreplicates')

    measurementContexts: Mapped[List['MeasurementContext']] = relationship(
        back_populates='bioreplicate',
        cascade='all, delete-orphan'
    )
    measurements: Mapped[List['Measurement']] = relationship(
        order_by='Measurement.timeInSeconds',
        secondary='MeasurementContexts',
        viewonly=True,
    )
