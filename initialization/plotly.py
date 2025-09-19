from plotly import graph_objects as go


def init_plotly():
    """
    A hack that fixes a plotly bug by initializing it before usage

    Community issue (from 2021):
    https://community.plotly.com/t/valueerror-invalid-value-in-basedatatypes-py/55993

    Github fix:
    https://github.com/plotly/plotly.py/issues/3441#issuecomment-1271747147
    """
    go.Figure(layout=dict(template='plotly'))
