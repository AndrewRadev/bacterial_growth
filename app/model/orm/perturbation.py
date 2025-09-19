from typing import Optional

import sqlalchemy as sql
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)
from sqlalchemy.ext.hybrid import hybrid_property

from app.model.orm.orm_base import OrmBase


class Perturbation(OrmBase):
    """
    The description of a change over time in a particular experiment's environment.

    A perturbation is described by the addition or removal of a ``Compartment``
    to the experiment or by the change from one ``Community`` to another.

    This may be changed in the future as we collect more studies with perturbations.
    """

    __tablename__ = 'Perturbations'

    id:          Mapped[int] = mapped_column(primary_key=True)
    description: Mapped[str] = mapped_column(sql.String)

    experimentId: Mapped[str] = mapped_column(sql.ForeignKey('Experiments.publicId'), nullable=False)
    experiment: Mapped['Experiment'] = relationship(back_populates='perturbations')

    study: Mapped['Study'] = relationship(
        secondary='Experiments',
        viewonly=True,
    )

    startTimeInSeconds: Mapped[int] = mapped_column(sql.Integer, nullable=False)
    endTimeInSeconds:   Mapped[int] = mapped_column(sql.Integer, nullable=False)

    removedCompartmentId: Mapped[int] = mapped_column(sql.ForeignKey('Compartments.id'))
    addedCompartmentId:   Mapped[int] = mapped_column(sql.ForeignKey('Compartments.id'))
    oldCommunityId:       Mapped[int] = mapped_column(sql.ForeignKey('Communities.id'))
    newCommunityId:       Mapped[int] = mapped_column(sql.ForeignKey('Communities.id'))

    oldCommunity:       Mapped[Optional['Community']]   = relationship(foreign_keys=[oldCommunityId])
    newCommunity:       Mapped[Optional['Community']]   = relationship(foreign_keys=[newCommunityId])
    removedCompartment: Mapped[Optional['Compartment']] = relationship(foreign_keys=[removedCompartmentId])
    addedCompartment:   Mapped[Optional['Compartment']] = relationship(foreign_keys=[addedCompartmentId])

    @hybrid_property
    def startTimeInHours(self):
        return self.startTimeInSeconds / 3600

    @hybrid_property
    def endTimeInHours(self):
        return self.endTimeInSeconds and self.endTimeInSeconds / 3600
