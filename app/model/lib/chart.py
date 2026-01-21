import math

import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

from app.model.lib.conversion import (
    convert_df_units,
    CELL_COUNT_UNITS,
    CFU_COUNT_UNITS,
    METABOLITE_UNITS,
)

PLOTLY_TEMPLATE = 'plotly_white'
"List of templates can be found at plotly.com/python/templates"


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
        self.clamp_x_data     = clamp_x_data
        self.show_std         = show_std

        self.log_left  = log_left
        self.log_right = log_right

        self.data_left  = []
        self.data_right = []

        self.mixed_units_left  = False
        self.mixed_units_right = False

        self.model_df_left_indices  = []
        self.model_df_right_indices = []

        self.regions = []

    def add_df(self, df, *, units, label=None, axis='left', metabolite_mass=None):
        if 'std' not in df:
            df['std'] = [float('nan') for _ in range(df['value'].size)]

        entry = (df, units, label, metabolite_mass)

        if axis == 'left':
            self.data_left.append(entry)
        elif axis == 'right':
            self.data_right.append(entry)
        else:
            raise ValueError(f"Unexpected axis: {axis}")

    def add_model_df(self, df, *, units, label=None, axis='left'):
        entry = (df, units, label, None)

        if axis == 'left':
            self.model_df_left_indices.append(len(self.data_left))
            self.data_left.append(entry)
        elif axis == 'right':
            self.model_df_right_indices.append(len(self.data_right))
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

        for (df, label) in converted_data_left:
            scatter_params = self._get_scatter_params(df, label, log=self.log_left)
            fig.add_trace(go.Scatter(**scatter_params), secondary_y=False)

        for (df, label) in converted_data_right:
            scatter_params = self._get_scatter_params(df, label, log=self.log_right)
            scatter_params = dict(**scatter_params, line={'dash': 'dot'})

            fig.add_trace(go.Scatter(**scatter_params), secondary_y=True)

        if self.clamp_x_data:
            # Fit the x-axis of the shortest chart:
            xaxis_range = self._calculate_x_range(converted_data_left + converted_data_right)
        else:
            xaxis_range = None

        left_yaxis_range  = self._calculate_y_range(
            converted_data_left,
            model_df_indices=self.model_df_left_indices,
            log=self.log_left,
        )
        right_yaxis_range = self._calculate_y_range(
            converted_data_right,
            model_df_indices=self.model_df_right_indices,
            log=self.log_right,
        )

        if self.regions:
            # No log-transformation applied for the region-drawing:
            y0, y1 = self._calculate_y_range(converted_data_left, self.model_df_left_indices)

            for index, (x0, x1, label, text) in enumerate(self.regions):
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

        left_yaxis = dict(
            side="left",
            title_text=left_units_label,
            exponentformat="power",
            range=left_yaxis_range,
        )
        if self.log_left:
            left_yaxis['type'] = 'log'

        right_yaxis = dict(
            side="right",
            title_text=right_units_label,
            exponentformat="power",
            range=right_yaxis_range,
        )
        if self.log_right:
            right_yaxis['type'] = 'log'

        fig.update_layout(
            showlegend=True,
            template=PLOTLY_TEMPLATE,
            margin=dict(l=0, r=0, t=60, b=40),
            title=dict(x=0),
            hovermode='x unified',
            legend=dict(
                yanchor="bottom",
                y=1,
                xanchor="left",
                x=0,
                orientation='h',
                maxheight=0.25,
                entrywidthmode='fraction',
                entrywidth=0.9,
            ),
            modebar=dict(orientation='v'),
            font_family="Public Sans",
            yaxis=left_yaxis,
            yaxis2=right_yaxis,
            xaxis=dict(
                title=dict(text='Time (h)'),
                range=xaxis_range,
            )
        )

        return fig.to_html(
            full_html=False,
            include_plotlyjs=False,
            default_width=(f"{self.width}px" if self.width is not None else '100%'),
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
                result_units = convert_df_units(df, units, self.cell_count_units)
                converted_units.add(result_units)
            elif units in CFU_COUNT_UNITS:
                result_units = convert_df_units(df, units, self.cfu_count_units)
                converted_units.add(result_units)
            elif units in METABOLITE_UNITS:
                result_units = convert_df_units(df, units, self.metabolite_units, metabolite_mass)
                converted_units.add(result_units)
            else:
                converted_units.add(units)

        if len(converted_units) > 1 or len(converted_data) == 0:
            return converted_data, '[mixed units]'

        return converted_data, tuple(converted_units)[0]

    def _get_scatter_params(self, df, label, log=False):
        value = df['value']

        if self.show_std and 'std' in df:
            if df['std'].isnull().all():
                # STD values were blank, don't draw error bars
                error_y = None
            else:
                # We want to clip negative error bars to 0
                positive_err = df['std']
                negative_err = np.clip(df['std'], max=df['value'])

                if (positive_err == negative_err).all():
                    error_y = go.scatter.ErrorY(array=positive_err)
                else:
                    error_y = go.scatter.ErrorY(array=positive_err, arrayminus=negative_err)
        else:
            error_y = None

        return dict(
            x=df['time'],
            y=value,
            name=label,
            error_y=error_y,
        )

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

    def _calculate_y_range(self, data, model_df_indices, log=False):
        """
        Find the limit for the y axis, ignoring model dataframes, since they
        might have exponentials that shoot up.
        """
        global_max_y          = 0
        global_min_y          = math.inf
        global_positive_min_y = math.inf

        for (i, (df, _)) in enumerate(data):
            if i in model_df_indices:
                # A model's data might shoot up exponentially, so we don't
                # consider it for the chart range
                continue

            # We look for the min and max values + std in the dataframe:
            lowers = []
            uppers = []

            entries = zip(df['value'], df['std'], df['std'])

            for value, upper_std, lower_std in entries:
                # For some reason, pandas might give us a None here, or it might
                # give us a NaN
                if upper_std is None or math.isnan(upper_std):
                    upper_std = 0
                if lower_std is None or math.isnan(lower_std):
                    lower_std = 0

                uppers.append(value + upper_std)
                if log:
                    lowers.append(value - lower_std)
                else:
                    lowers.append(np.clip(value - lower_std, min=0))

            max_y = max(uppers)
            min_y = min(lowers)

            positive_ys = [y for y in lowers if y > 0]
            if positive_ys:
                positive_min_y = min(positive_ys)
            else:
                positive_min_y = None

            if max_y > global_max_y:
                global_max_y = max_y
            if min_y < global_min_y:
                global_min_y = min_y
            if positive_min_y is not None and positive_min_y < global_positive_min_y:
                global_positive_min_y = positive_min_y

        # The range of the chart is given a padding depending on the data range
        # to make sure the content is visible:
        padding = (global_max_y - global_min_y) * 0.05

        if log:
            # Fifth of an order of magnitude of padding:
            padding = 0.2
            global_max_y = np.log10(global_max_y)

            if global_min_y <= 0.0:
                global_min_y = np.log10(global_positive_min_y)
            else:
                global_min_y = np.log10(global_min_y)

        lower = global_min_y - padding
        upper = global_max_y + padding

        return [lower, upper]
