import sqlalchemy as sql
from sqlalchemy.orm import (
    mapped_column,
    relationship,
    Mapped,
)

from app.model.orm.orm_base import OrmBase


class CommunityStrain(OrmBase):
    "Join table between Communities and Strains"

    __tablename__ = "CommunityStrains"

    id: Mapped[int] = mapped_column(primary_key=True)

    communityId: Mapped[int] = mapped_column(sql.ForeignKey('Communities.id'))
    strainId:    Mapped[int] = mapped_column(sql.ForeignKey('Strains.id'))

    community: Mapped['Community'] = relationship(back_populates='communityStrains')
    strain:    Mapped['Strain']    = relationship(back_populates='communityStrains')
