import sqlalchemy as sql
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)
from sqlalchemy.ext.hybrid import hybrid_property

from app.model.orm.orm_base import OrmBase


class Perturbation(OrmBase):
    __tablename__ = 'Perturbations'

    id:          Mapped[int] = mapped_column(primary_key=True)
    description: Mapped[str] = mapped_column(sql.String)

    studyId: Mapped[str] = mapped_column(sql.ForeignKey('Studies.publicId'), nullable=False)
    study: Mapped['Study'] = relationship(back_populates='perturbations')

    experimentId: Mapped[int] = mapped_column(sql.ForeignKey('Experiments.id'), nullable=False)
    experiment: Mapped['Experiment'] = relationship(back_populates='perturbations')

    startTimeInSeconds: Mapped[int] = mapped_column(sql.Integer, nullable=False)
    endTimeInSeconds:   Mapped[int] = mapped_column(sql.Integer, nullable=False)

    removedCompartmentId: Mapped[int] = mapped_column(sql.ForeignKey('Compartments.id'))
    addedCompartmentId:   Mapped[int] = mapped_column(sql.ForeignKey('Compartments.id'))

    oldCommunityId: Mapped[int] = mapped_column(sql.ForeignKey('Communities.id'))
    newCommunityId: Mapped[int] = mapped_column(sql.ForeignKey('Communities.id'))

    @hybrid_property
    def startTimeInHours(self):
        return self.startTimeInSeconds / 3600

    @hybrid_property
    def endTimeInHours(self):
        return self.endTimeInSeconds and self.endTimeInSeconds / 3600
