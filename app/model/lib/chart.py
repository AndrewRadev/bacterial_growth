import math

import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

from app.model.lib.conversion import convert_measurement_units

PLOTLY_TEMPLATE = 'plotly_white'
"List of templates can be found at plotly.com/python/templates"

CELL_COUNT_UNITS = ('Cells/mL', 'Cells/μL')
"Units that measure number of cells per volume"

CFU_COUNT_UNITS  = ('CFUs/mL', 'CFUs/μL')
"Units that measure number of CFUs per volume"

METABOLITE_UNITS = ('mM', 'μM', 'nM', 'pM', 'g/L', 'mg/L')
"Units for metabolites, both molar and mass concentration"


class Chart:
    """
    An object that encapsulates the common properties of Plotly charts across
    the site.
    """

    def __init__(
        self,
        time_units,
        cell_count_units='Cells/mL',
        cfu_count_units='CFUs/mL',
        metabolite_units='mM',
        log_left=False,
        log_right=False,
        width=None,
        title=None,
        legend_position='top',
        clamp_x_data=False,
        show_std=True,
    ):
        # TODO (2025-06-25) Unused, should consider conversion, but handle
        # units during modeling:
        self.time_units       = time_units

        self.cell_count_units = cell_count_units
        self.cfu_count_units  = cfu_count_units
        self.metabolite_units = metabolite_units
        self.width            = width
        self.title            = title
        self.legend_position  = legend_position
        self.clamp_x_data     = clamp_x_data
        self.show_std         = show_std

        self.log_left  = log_left
        self.log_right = log_right

        self.data_left  = []
        self.data_right = []

        self.mixed_units_left  = False
        self.mixed_units_right = False

        self.model_df_indices = []
        self.regions          = []

    def add_df(self, df, *, units, label=None, axis='left', metabolite_mass=None):
        entry = (df, units, label, metabolite_mass)

        if axis == 'left':
            self.data_left.append(entry)
        elif axis == 'right':
            self.data_right.append(entry)
        else:
            raise ValueError(f"Unexpected axis: {axis}")

    def add_model_df(self, df, *, units, label=None, axis='left'):
        self.model_df_indices.append(len(self.data_left) + len(self.data_right))
        entry = (df, units, label, None)

        if axis == 'left':
            self.data_left.append(entry)
        elif axis == 'right':
            self.data_right.append(entry)
        else:
            raise ValueError(f"Unexpected axis: {axis}")

    def add_region(self, start_time, end_time, label, text):
        self.regions.append((start_time, end_time, label, text))

    def to_html(self):
        fig = make_subplots(specs=[[{"secondary_y": True}]])

        converted_data_left,  left_units_label  = self._convert_units(self.data_left)
        converted_data_right, right_units_label = self._convert_units(self.data_right)

        if left_units_label == '[mixed units]':
            self.mixed_units_left = True
        if right_units_label == '[mixed units]':
            self.mixed_units_right = True

        if self.log_left:
            left_units_label = f"ln({left_units_label})"
        if self.log_right:
            right_units_label = f"ln({right_units_label})"

        for (df, label) in converted_data_left:
            scatter_params = self._get_scatter_params(df, label, log=self.log_left)
            fig.add_trace(go.Scatter(**scatter_params), secondary_y=False)

        for (df, label) in converted_data_right:
            scatter_params = self._get_scatter_params(df, label, log=self.log_right)
            scatter_params = dict(**scatter_params, line={'dash': 'dot'})

            fig.add_trace(go.Scatter(**scatter_params), secondary_y=True)

        xaxis_range       = self._calculate_x_range(converted_data_left + converted_data_right)
        left_yaxis_range  = self._calculate_y_range(converted_data_left)
        right_yaxis_range = self._calculate_y_range(converted_data_right)

        for index, (x0, x1, label, text) in enumerate(self.regions):
            y0, y1 = left_yaxis_range

            fig.add_trace(
                go.Scatter(
                    name=label,
                    x=[x0, x0, x1, x1, x0],
                    y=[y0, y0, y0, y1, y1],
                    opacity=0.15,
                    line_width=0,
                    fill="toself",
                    hovertemplate=text,
                    mode="text",
                ),
            )

        fig.update_yaxes(title_text=left_units_label,  secondary_y=False)
        fig.update_yaxes(title_text=right_units_label, secondary_y=True)

        if self.title:
            title = dict(text=self.title)
        else:
            title = dict(x=0)

        fig.update_layout(
            template=PLOTLY_TEMPLATE,
            margin=dict(l=0, r=0, t=60, b=40),
            title=title,
            hovermode='x unified',
            legend=dict(yanchor="bottom", y=1, xanchor="left", x=0, orientation='h'),
            modebar=dict(orientation='v'),
            font_family="Public Sans",
            yaxis=dict(
                exponentformat="power",
                side="left",
                range=left_yaxis_range,
            ),
            yaxis2=dict(
                exponentformat="power",
                side="right",
                range=right_yaxis_range,
            ),
            xaxis=dict(
                title=dict(text='Time (h)'),
                range=xaxis_range,
            )
        )

        return fig.to_html(
            full_html=False,
            include_plotlyjs=False,
            default_width=(f"{self.width}px" if self.width is not None else None),
            config={
                'toImageButtonOptions': {
                    'format': 'svg',
                    'filename': 'mgrowth_chart',
                    # Force width and height to be the same as the visible dimensions on screen
                    # Reference: https://github.com/plotly/plotly.js/pull/3746
                    'height': None,
                    'width': None,
                },
            },
        )

    def _convert_units(self, data):
        if len(data) == 0:
            return [], None

        converted_units = set()
        converted_data = [(df, label) for (df, _, label, _) in data]

        for (df, units, label, metabolite_mass) in data:
            if units in CELL_COUNT_UNITS:
                result_units = self._convert_df_units(df, units, self.cell_count_units)
                converted_units.add(result_units)
            elif units in CFU_COUNT_UNITS:
                result_units = self._convert_df_units(df, units, self.cfu_count_units)
                converted_units.add(result_units)
            elif units in METABOLITE_UNITS:
                result_units = self._convert_df_units(df, units, self.metabolite_units, metabolite_mass)
                converted_units.add(result_units)
            else:
                converted_units.add(units)

        if len(converted_units) > 1 or len(converted_data) == 0:
            return converted_data, '[mixed units]'

        return converted_data, tuple(converted_units)[0]

    def _get_scatter_params(self, df, label, log=False):
        if self.show_std and 'std' in df:
            if df['std'].isnull().all():
                # STD values were blank, don't draw error bars
                error_y = None
            else:
                # We want to clip negative error bars to 0, except in log-view:
                positive_err = df['std']
                negative_err = np.clip(df['std'], max=df['value'])

                if log or (positive_err == negative_err).all():
                    error_y = go.scatter.ErrorY(array=positive_err)
                else:
                    error_y = go.scatter.ErrorY(array=positive_err, arrayminus=negative_err)
        else:
            error_y = None

        return dict(
            x=df['time'],
            y=df['value'],
            name=label,
            error_y=error_y,
        )

    def _convert_df_units(self, df, source_units, target_units, metabolite_mass=None):
        new_value = convert_measurement_units(
            df['value'],
            source_units,
            target_units,
            mass=metabolite_mass,
        )

        if new_value is not None:
            df['value'] = new_value
            if 'std' in df:
                df['std'] = convert_measurement_units(
                    df['std'],
                    source_units,
                    target_units,
                    mass=metabolite_mass,
                )
            return target_units
        else:
            return source_units

    def _calculate_x_range(self, data):
        # With multiple charts, fit the x-axis of the shortest one:
        global_max_x = math.inf
        global_min_x = 0

        for (i, (df, _)) in enumerate(data):
            max_x = df['time'].max()
            min_x = df['time'].min()

            if max_x < global_max_x:
                global_max_x = max_x
            if min_x > global_min_x:
                global_min_x = min_x

        # The range of the chart is given a padding depending on the data range
        # to make sure the content is visible:
        padding = (global_max_x - global_min_x) * 0.05
        return [global_min_x - padding, global_max_x + padding]

    def _calculate_y_range(self, data):
        """
        Find the limit for the y axis, ignoring model dataframes, since they
        might have exponentials that shoot up.
        """
        global_max_y = 0
        global_min_y = math.inf

        for (i, (df, _)) in enumerate(data):
            if i in self.model_df_indices:
                # A model's data might shoot up exponentially, so we don't
                # consider it for the chart range
                continue

            # We look for the min and max values in the dataframe and their
            # corresponding standard deviation:
            min_value = df['value'].min()
            max_value = df['value'].max()

            min_row = df[df['value'] == min_value]
            max_row = df[df['value'] == max_value]

            min_std = min_row['std'].iloc[0]
            max_std = max_row['std'].iloc[0]

            # For some reason, pandas might give us a None here, or it might
            # give us a NaN
            if min_std is None or math.isnan(min_std):
                min_std = 0
            if max_std is None or math.isnan(max_std):
                max_std = 0

            max_y = max_value + max_std
            min_y = min_value - min_std

            if max_y > global_max_y:
                global_max_y = max_y
            if min_y < global_min_y:
                global_min_y = min_y

        # The range of the chart is given a padding depending on the data range
        # to make sure the content is visible:
        padding = (global_max_y - global_min_y) * 0.05
        return [global_min_y - padding, global_max_y + padding]
