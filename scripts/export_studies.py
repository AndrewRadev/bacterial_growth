import os
from pathlib import Path

import simplejson as json
import sqlalchemy as sql

from db import get_session
from app.model.orm import Study

with get_session() as db_session:
    studies = db_session.scalars(
        sql.select(Study)
        .where(Study.isPublished)
        .order_by(Study.publicId)
    ).all()

    for study in studies:
        base_dir = Path(f"static/export/{study.publicId}")
        base_dir.mkdir(parents=True, exist_ok=True)

        submission = study.find_last_submission(db_session)

        # Export study design:
        with open(base_dir / 'study_design.json', 'w') as f:
            json.dump(submission.studyDesign, f, use_decimal=True, indent=2)

        # Export data files:
        for name, df in submission.dataFile.extract_sheets().items():
            file_name = '_'.join(name.lower().split()) + '.csv'
            df.to_csv(base_dir / file_name, index=False)
