import sqlalchemy as sql
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from app.model.orm.orm_base import OrmBase


class ExperimentCompartment(OrmBase):
    __tablename__ = 'ExperimentCompartments'

    id: Mapped[int] = mapped_column(sql.Integer, primary_key=True)

    experimentId:  Mapped[str] = mapped_column(sql.ForeignKey('Experiments.publicId'))
    compartmentId: Mapped[int] = mapped_column(sql.ForeignKey('Compartments.id'))

    experiment:  Mapped['Experiment']  = relationship(back_populates="experimentCompartments")
    compartment: Mapped['Compartment'] = relationship(back_populates="experimentCompartments")
