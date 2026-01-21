import pandas as pd

from flask import (
    g,
    render_template,
    redirect,
    request,
)
from app.model.lib.chart import Chart
from app.model.lib.errors import LoginRequired

# TODO (2026-01-21) validate files, show errors

def sandbox_index_page():
    chart = Chart(time_units='h')

    for file in request.files.getlist('data-left'):
        df = pd.read_csv(file)
        chart.add_df(df, units='TODO', label=file.filename, axis='left')

    return render_template('pages/sandbox/index.html', chart=chart)
