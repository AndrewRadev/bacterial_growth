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

    for axis in ('left', 'right'):
        for file in request.files.getlist(f"data-{axis}"):
            try:
                df = pd.read_csv(file)
            except pd.errors.EmptyDataError:
                continue

            c1 = df.columns[0]
            c2 = df.columns[1]
            if len(df.columns) > 2:
                c3 = df.columns[2]
            else:
                c3 = None

            label = f"{file.filename}: {c2}"
            units = request.form.get(f"units-{axis}")

            df = df.rename(columns={c1: "time", c2: "value", c3: "std"})

            chart.add_df(df, units=units, label=label, axis=axis)

    return render_template('pages/sandbox/index.html', chart=chart)
