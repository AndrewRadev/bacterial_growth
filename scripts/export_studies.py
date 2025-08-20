from pathlib import Path
from datetime import datetime, UTC

import sqlalchemy as sql
from long_task_printer import print_with_time

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
        with print_with_time(f"> Exporting study {study.publicId}"):
            submission = study.find_last_submission(db_session)
            submission.export_data(message="Full export", timestamp=timestamp)
