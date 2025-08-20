from flask import (
    g,
    session,
    redirect,
    url_for,
)
import sqlalchemy as sql
from werkzeug.exceptions import Forbidden

from app.model.orm import Submission


def new_submission_action():
    if 'submission_id' in session:
        del session['submission_id']

    return redirect(url_for('upload_step1_page'))


def edit_submission_action(id):
    session['submission_id'] = id

    return redirect(url_for('upload_status_page'))


def delete_submission_action(id):
    if not g.current_user:
        raise Forbidden

    submission = g.db_session.get(Submission, id)

    if submission.userUniqueID != g.current_user.uuid:
        raise Forbidden

    if 'submission_id' in session and session['submission_id'] == id:
        del session['submission_id']

    g.db_session.execute(sql.delete(Submission).where(Submission.id == id))
    g.db_session.commit()

    return redirect(url_for('upload_status_page'))
