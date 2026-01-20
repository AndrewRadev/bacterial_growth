from flask import (
    g,
    render_template,
    redirect,
)
from app.model.lib.errors import LoginRequired


def sandbox_index_page():
    if not g.current_user:
        raise LoginRequired()

    return render_template('pages/sandbox/index.html')
