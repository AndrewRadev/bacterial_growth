import sqlalchemy as sql

from db import get_session
from app.model.orm import User
from app.model.lib.dev import bootstrap_study

STUDY_KEYS = [
    'synthetic_gut',
    'starvation_responses',
    'ri_bt_bh_in_chemostat_controls',
    'integrated_culturing',
]

with get_session() as db_session:
    user = db_session.scalars(
        sql.select(User)
        .where(User.isAdmin)
        .order_by(User.createdAt.asc())
        .limit(1)
    ).one_or_none()

    if user is None:
        print("No admin user found in database, please create one before creating studies")
        exit(1)

    for study_key in STUDY_KEYS:
        bootstrap_study(db_session, study_key, user.uuid)

print(f"> Records created, owned by user with ID: {user.uuid} ({user.name})")
