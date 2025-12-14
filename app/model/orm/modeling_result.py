import re
from datetime import datetime

import numpy as np
import pandas as pd
import sqlalchemy as sql
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
    validates,
)
from sqlalchemy_utc.sqltypes import UtcDateTime

from app.model.orm.orm_base import OrmBase

MODEL_NAMES = {
    'easy_linear':     '"Easy linear" method',
    'logistic':        'Logistic model',
    'baranyi_roberts': 'Baranyi-Roberts model',
}
"The human-readable names of the supported models/methods"

_VALID_TYPES = [
    'easy_linear',
    'logistic',
    'baranyi_roberts',
]
_VALID_STATES = [
    'pending',
    'ready',
    'error',
]


class ModelingResult(OrmBase):
    """
    The results of fitting a model onto a set of measurements.

    The measurements are represented by a ``ModelingContext`` and the results
    of the calculation are stored in the ``params`` field. The ``state`` of the
    record describes the status of the job that runs the calculations.
    """

    __tablename__ = "ModelingResults"

    id:   Mapped[int] = mapped_column(primary_key=True)
    type: Mapped[str] = mapped_column(sql.String(100), nullable=False)

    measurementContextId: Mapped[int] = mapped_column(
        sql.ForeignKey('MeasurementContexts.id'),
        nullable=False,
    )
    measurementContext: Mapped['MeasurementContext'] = relationship(back_populates='modelingResults')

    customModelId: Mapped[int] = mapped_column(sql.ForeignKey('CustomModels.id'))
    customModel: Mapped['CustomModel'] = relationship()

    params: Mapped[sql.JSON] = mapped_column(sql.JSON, nullable=False)

    state:    Mapped[str] = mapped_column(sql.String(100), default='pending')
    error:    Mapped[str] = mapped_column(sql.String)
    rSummary: Mapped[str] = mapped_column(sql.String)

    createdAt:    Mapped[datetime] = mapped_column(UtcDateTime, server_default=sql.FetchedValue())
    updatedAt:    Mapped[datetime] = mapped_column(UtcDateTime, server_default=sql.FetchedValue())
    calculatedAt: Mapped[datetime] = mapped_column(UtcDateTime)

    # For custom models:
    xValues: Mapped[sql.JSON] = mapped_column(sql.JSON, nullable=False)
    yValues: Mapped[sql.JSON] = mapped_column(sql.JSON, nullable=False)
    yErrors: Mapped[sql.JSON] = mapped_column(sql.JSON, nullable=False)

    @validates('type')
    def _validate_type(self, key, value):
        if re.fullmatch('custom_\d+', value):
            return value
        else:
            return self._validate_inclusion(key, value, _VALID_TYPES)

    @validates('state')
    def _validate_state(self, key, value):
        return self._validate_inclusion(key, value, _VALID_STATES)

    @classmethod
    def empty_params(Self, model_type):
        if model_type == 'easy_linear':
            inputs = {'pointCount': '5'}
            coefficients = {
                'y0':    None,
                'y0_lm': None,
                'mumax': None,
                'lag':   None,
            }
        elif model_type == 'logistic':
            inputs = {'endTime': ''}
            coefficients = {
                'y0':    None,
                'mumax': None,
                'K':     None,
            }
        elif model_type == 'baranyi_roberts':
            inputs = {'endTime': ''}
            coefficients = {
                'y0':    None,
                'mumax': None,
                'K':     None,
                'h0':    None,
            }
        elif model_type.startswith('custom_'):
            inputs = {}
            coefficients = {
                'mumax': None,
                'lag':   None,
                'K':     None,
            }
        else:
            raise ValueError(f"Don't know what the coefficients are for model type: {repr(model_type)}")

        return {
            'coefficients': coefficients,
            'inputs': inputs,
            'fit': {
                'r2': None,
                'rss': None,
            }
        }

    @property
    def model_name(self):
        if self.type.startswith('custom_'):
            return self.customModel.name
        else:
            return MODEL_NAMES[self.type]

    def generate_chart_df(self, measurements_df):
        start_time = measurements_df['time'].min()
        end_time   = measurements_df['time'].max()

        if self.type.startswith('custom_'):
            timepoints = self.xValues
            values     = self.yValues
            errors     = self.yErrors
        else:
            timepoints = np.linspace(start_time, end_time, 200)
            values     = self._predict(timepoints)
            errors     = []

        return pd.DataFrame.from_dict({
            'time':   timepoints,
            'value':  values,
            'errors': stds,
        })

    def _predict(self, timepoints):
        if self.type == 'easy_linear':
            return self._predict_easy_linear(timepoints)
        elif self.type == 'logistic':
            return self._predict_logistic(timepoints)
        elif self.type == 'baranyi_roberts':
            return self._predict_baranyi_roberts(timepoints)
        else:
            raise ValueError(f"Don't know how to predict values for model type: {repr(self.type)}")

    def _predict_easy_linear(self, time):
        coefficients = self.params['coefficients']

        # y0    = float(coefficients['y0'])
        y0_lm = float(coefficients['y0_lm'])
        mumax = float(coefficients['mumax'])
        # lag   = float(coefficients['lag'])

        # No lag:
        # return y0 * np.exp(time * mumax)

        # Exponential:
        return y0_lm * np.exp(time * mumax)

    def _predict_logistic(self, time):
        coefficients = self.params['coefficients']

        y0    = float(coefficients['y0'])
        mumax = float(coefficients['mumax'])
        K     = float(coefficients['K'])

        return (K * y0)/(y0 + (K - y0) * np.exp(-mumax * time))

    def _predict_baranyi_roberts(self, time):
        coefficients = self.params['coefficients']

        y0    = float(coefficients['y0'])
        mumax = float(coefficients['mumax'])
        K     = float(coefficients['K'])
        h0    = float(coefficients['h0'])

        # Formula taken from the "growthrates" documentation under `grow_baranyi`:
        # https://cran.r-project.org/web/packages/growthrates/growthrates.pdf
        #
        A = time + 1/mumax * np.log(np.exp(-mumax * time) + np.exp(-h0) - np.exp(-mumax * time - h0))
        log_y = np.log(y0) + mumax * A - np.log(1 + (np.exp(mumax * A) - 1)/np.exp(np.log(K) - np.log(y0)))

        return np.exp(log_y)
