import os
from pathlib import Path
from datetime import datetime, UTC

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

    timestamp = datetime.now(UTC)

    for study in studies:
        base_dir = Path(f"static/export/{study.publicId}")
        base_dir.mkdir(parents=True, exist_ok=True)

        submission = study.find_last_submission(db_session)

        # Clean up previous files:
        for file in base_dir.glob('*.csv'):
            file.unlink()
        for file in base_dir.glob('*.json'):
            file.unlink()

        # Export study design:
        with open(base_dir / 'study_design.json', 'w') as f:
            json.dump(submission.studyDesign, f, use_decimal=True, indent=2)

        # Export data files:
        for name, df in submission.dataFile.extract_sheets().items():
            file_name = '_'.join(name.lower().split()) + '.csv'
            df.to_csv(base_dir / file_name, index=False)

        # Record a changelog entry
        with open(base_dir / 'changes.log', 'a') as f:
            print(f"[{timestamp.isoformat()}] Full export", file=f)
