import sqlalchemy as sql
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from app.model.orm.orm_base import OrmBase


class ProjectUser(OrmBase):
    """
    Join table between Projects and Users.

    The users recorded in this table have the ability to manage a particular
    project, add studies to it.
    """

    __tablename__ = 'ProjectUsers'

    id: Mapped[int] = mapped_column(sql.Integer, primary_key=True)

    projectUniqueID: Mapped[str] = mapped_column(sql.ForeignKey('Projects.uuid'), nullable=False)
    userUniqueID:    Mapped[str] = mapped_column(sql.ForeignKey('Users.uuid'),    nullable=False)

    project: Mapped['Project'] = relationship(back_populates="projectUsers")
    user:    Mapped['User']    = relationship(back_populates="projectUsers")
