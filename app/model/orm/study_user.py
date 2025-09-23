import sqlalchemy as sql
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from app.model.orm.orm_base import OrmBase


class StudyUser(OrmBase):
    """
    Join table between Studies and Users.

    The users recorded in this table have the ability to manage a particular
    study, to update it, or to reuse its components in other uploads.
    """

    __tablename__ = 'StudyUsers'

    id: Mapped[int] = mapped_column(sql.Integer, primary_key=True)

    studyUniqueID: Mapped[str] = mapped_column(sql.ForeignKey('Studies.uuid'), nullable=False)
    userUniqueID:  Mapped[str] = mapped_column(sql.ForeignKey('Users.uuid'),   nullable=False)

    study: Mapped['Study'] = relationship(back_populates="studyUsers")
    user:  Mapped['User']  = relationship(back_populates="studyUsers")
