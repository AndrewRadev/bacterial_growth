import pandas as pd

from flask import (
    g,
    render_template,
    redirect,
    request,
)
from app.model.lib.chart import Chart
from app.model.lib.errors import LoginRequired

def sandbox_index_page():
    chart = Chart(time_units='h')
    errors = {}

    for axis in ('left', 'right'):
        for file in request.files.getlist(f"data-{axis}"):
            if file.filename == '':
                continue

            try:
                df = pd.read_csv(file)
            except pd.errors.EmptyDataError:
                errors[file.filename] = "No columns found in file"
                continue

            if len(df.columns) < 2:
                errors[file.filename] = f"Expected at least 2 columns, found {len(df.columns)}"
                continue

            c1 = df.columns[0]
            c2 = df.columns[1]
            if len(df.columns) > 2:
                c3 = df.columns[2]
            else:
                c3 = None

            label = f"<b>{file.filename}</b>: {c2}"
            units = request.form.get(f"units-{axis}")

            df.rename(columns={c1: "time", c2: "value", c3: "std"}, inplace=True)

            chart.add_df(df, units=units, label=label, axis=axis)

    return render_template(
        'pages/sandbox/index.html',
        chart=chart,
        errors=errors,
    )
