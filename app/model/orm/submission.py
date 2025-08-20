from typing import Optional
from datetime import datetime, UTC
from pathlib import Path

import simplejson as json
import sqlalchemy as sql
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)
from sqlalchemy_utc.sqltypes import UtcDateTime

from app.model.orm.orm_base import OrmBase


class Submission(OrmBase):
    __tablename__ = 'Submissions'

    id: Mapped[int] = mapped_column(primary_key=True)

    projectUniqueID: Mapped[str] = mapped_column(sql.String(100), nullable=False)
    studyUniqueID:   Mapped[str] = mapped_column(sql.String(100), nullable=False)

    project: Mapped[Optional['Project']] = relationship(
        foreign_keys=[projectUniqueID],
        primaryjoin="Submission.projectUniqueID == Project.uuid",
    )
    study: Mapped[Optional['Study']] = relationship(
        foreign_keys=[studyUniqueID],
        primaryjoin="Submission.studyUniqueID == Study.uuid",
    )

    userUniqueID: Mapped[str] = mapped_column(sql.ForeignKey('Users.uuid'), nullable=False)
    user: Mapped['User'] = relationship(back_populates='submissions')

    studyDesign: Mapped[sql.JSON] = mapped_column(sql.JSON, nullable=False)

    dataFileId: Mapped[int] = mapped_column(sql.ForeignKey('ExcelFiles.id'), nullable=True)
    dataFile: Mapped[Optional['ExcelFile']] = relationship(
        foreign_keys=[dataFileId],
        cascade='all, delete-orphan',
        single_parent=True,
    )

    createdAt: Mapped[datetime] = mapped_column(UtcDateTime, server_default=sql.FetchedValue())
    updatedAt: Mapped[datetime] = mapped_column(UtcDateTime, server_default=sql.FetchedValue())

    @property
    def completed_step_count(self):
        return sum([
            1 if self.projectUniqueID and self.studyUniqueID else 0,
            1 if len(self.studyDesign.get('strains', [])) + len(self.studyDesign.get('custom_strains', [])) > 0 else 0,
            1 if len(self.studyDesign.get('techniques', [])) > 0 else 0,
            1 if len(self.studyDesign.get('compartments', [])) > 0 and len(self.studyDesign.get('communities', [])) > 0 else 0,
            1 if len(self.studyDesign.get('experiments', [])) > 0 else 0,
            1 if self.dataFileId else 0,
            1 if self.study and self.study.isPublished else 0,
        ])

    @property
    def is_finished(self):
        return self.completed_step_count == 7

    def build_techniques(self):
        from app.model.orm import MeasurementTechnique
        return [MeasurementTechnique(**m) for m in self.studyDesign['techniques']]

    def export_data(self, message, timestamp=None):
        assert(self.study is not None)
        assert(self.study.isPublished)

        if timestamp is None:
            timestamp = datetime.now(UTC)

        base_dir = Path(f"static/export/{self.study.publicId}")
        base_dir.mkdir(parents=True, exist_ok=True)

        # Clean up previous files:
        for file in base_dir.glob('*.csv'):
            file.unlink()
        for file in base_dir.glob('*.json'):
            file.unlink()

        # Export study design:
        with open(base_dir / 'study_design.json', 'w') as f:
            json.dump(self.studyDesign, f, use_decimal=True, indent=2)

        # Export data files:
        for name, df in self.dataFile.extract_sheets().items():
            file_name = '_'.join(name.lower().split()) + '.csv'
            df.to_csv(base_dir / file_name, index=False)

        # Record a changelog entry
        with open(base_dir / 'changes.log', 'a') as f:
            print(f"[{timestamp.isoformat()}] {message}", file=f)
