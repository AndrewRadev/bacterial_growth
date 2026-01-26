import sqlalchemy as sql

from app.model.lib.db import execute_into_df
from app.model.lib.chart import Chart
from app.model.orm import (
    Bioreplicate,
    Experiment,
    Measurement,
    MeasurementContext,
    ModelingResult,
    Perturbation,
)


class ComparativeChartForm:
    def __init__(
        self,
        db_session,
        time_units='h',
        left_axis_ids=[],
        right_axis_ids=[],
        left_axis_model_ids=[],
        right_axis_model_ids=[],
        show_std=True,
        show_perturbations=True,
    ):
        self.db_session         = db_session
        self.time_units         = time_units
        self.show_std           = show_std
        self.show_perturbations = show_perturbations

        self.left_axis_ids  = set(left_axis_ids)
        self.right_axis_ids = set(right_axis_ids)

        self.left_axis_model_ids  = set(left_axis_model_ids)
        self.right_axis_model_ids = set(right_axis_model_ids)

        self.measurement_context_ids = list(self.left_axis_ids) + list(self.right_axis_ids)
        self.measurement_contexts = []

        self.modeling_result_ids = list(self.left_axis_model_ids) + list(self.right_axis_model_ids)
        self.modeling_results = []

        self.cell_count_units = 'Cells/mL'
        self.cfu_count_units  = 'CFUs/mL'
        self.metabolite_units = 'mM'

        self.log_left  = False
        self.log_right = False

    def build_chart(self, args=None, width=None, clamp_x_data=False):
        if args:
            self._extract_args(args)

        chart = Chart(
            time_units=self.time_units,
            cell_count_units=self.cell_count_units,
            cfu_count_units=self.cfu_count_units,
            metabolite_units=self.metabolite_units,
            log_left=self.log_left,
            log_right=self.log_right,
            width=width,
            clamp_x_data=clamp_x_data,
            show_std=self.show_std,
        )

        self.measurement_contexts = self.db_session.scalars(
            sql.select(MeasurementContext)
            .where(MeasurementContext.id.in_(self.measurement_context_ids))
            .options(
                sql.orm.selectinload(MeasurementContext.technique),
                sql.orm.selectinload(MeasurementContext.bioreplicate),
            )
        ).all()

        self.modeling_results = self.db_session.scalars(
            sql.select(ModelingResult)
            .where(ModelingResult.id.in_(self.modeling_result_ids))
            .options(
                sql.orm.selectinload(ModelingResult.measurementContext),
                sql.orm.selectinload(ModelingResult.measurementContext, MeasurementContext.technique),
            )
        ).all()

        measurements_df = self.get_measurements_df(self.measurement_context_ids)

        for measurement_context in self.measurement_contexts:
            technique = measurement_context.technique

            if measurement_context.id in self.right_axis_ids:
                axis = 'right'
                log_transform = self.log_right
            else:
                axis = 'left'
                log_transform = self.log_left

            measurement_df = measurements_df[measurements_df['contextId'] == measurement_context.id]
            label = measurement_context.get_chart_label()

            if technique.subjectType == 'metabolite':
                subject = measurement_context.get_subject(self.db_session)
                metabolite_mass = subject.averageMass
            else:
                metabolite_mass = None

            if technique.units == '':
                units = technique.short_name
            else:
                units = technique.units

            chart.add_df(
                measurement_df,
                units=units,
                label=label,
                axis=axis,
                metabolite_mass=metabolite_mass,
            )

        for modeling_result in self.modeling_results:
            measurement_context = modeling_result.measurementContext
            technique = measurement_context.technique

            if modeling_result.id in self.right_axis_model_ids:
                axis = 'right'
                log_transform = self.log_right
            else:
                axis = 'left'
                log_transform = self.log_left

            measurement_df = measurements_df[measurements_df['contextId'] == measurement_context.id]
            if measurement_df.empty:
                # Could happen if we're just rendering the model without the parent measurement:
                measurement_df = measurement_context.get_df(self.db_session)

            model_df = modeling_result.generate_chart_df(measurement_df)
            label    = modeling_result.get_chart_label()

            if technique.units == '':
                units = technique.short_name
            else:
                units = technique.units

            chart.add_model_df(
                model_df,
                units=units,
                label=label,
                axis=axis,
            )

        if self.show_perturbations:
            perturbations = self.db_session.scalars(
                sql.select(Perturbation)
                .distinct()
                .join(Experiment)
                .join(Bioreplicate)
                .join(MeasurementContext)
                .where(MeasurementContext.id.in_(self.measurement_context_ids))
                .order_by(Perturbation.startTimeInSeconds)
            ).all()

            for i, perturbation in enumerate(perturbations):
                chart.add_region(
                    start_time=perturbation.startTimeInHours,
                    end_time=perturbation.endTimeInHours,
                    label=f"Perturbation {i + 1} (<b>{perturbation.experiment.name}</b>)",
                    text=perturbation.description,
                )

        return chart

    @property
    def permalink_query(self):
        if len(self.measurement_contexts):
            experiment_id = self.measurement_contexts[0].bioreplicate.experimentId
            technique_id  = self.measurement_contexts[0].techniqueId
        elif len(self.modeling_results):
            experiment_id = self.modeling_results[0].measurementContext.bioreplicate.experimentId
            technique_id  = self.modeling_results[0].measurementContext.techniqueId
        else:
            experiment_id = ''
            technique_id = ''

        parts = {
            'l':  ','.join([str(i) for i in sorted(self.left_axis_ids)]),
            'r':  ','.join([str(i) for i in sorted(self.right_axis_ids)]),
            'lm': ','.join([str(i) for i in sorted(self.left_axis_model_ids)]),
            'rm': ','.join([str(i) for i in sorted(self.right_axis_model_ids)]),

            'selectedExperimentId': str(experiment_id),
            'selectedTechniqueId':  str(technique_id),
        }

        return '&'.join([f"{k}={v}" for k, v in parts.items() if v != ''])

    def _extract_args(self, args):
        self.left_axis_ids  = set()
        self.right_axis_ids = set()

        self.left_axis_model_ids  = set()
        self.right_axis_model_ids = set()

        self.log_left  = False
        self.log_right = False

        for arg, value in args.items():
            if arg.startswith('measurementContext|'):
                context_id = int(arg.removeprefix('measurementContext|'))
                self.measurement_context_ids.append(context_id)
                self.left_axis_ids.add(context_id)

            elif arg.startswith('modelingResult|'):
                modeling_result_id = int(arg.removeprefix('modelingResult|'))
                self.modeling_result_ids.append(modeling_result_id)
                self.left_axis_model_ids.add(modeling_result_id)

            elif arg.startswith('axis|'):
                record_type, record_id = arg.removeprefix('axis|').split('|')

                if value == 'left':
                    # Left axis by default
                    pass
                elif value == 'right':
                    if record_type == 'measurementContext':
                        context_id = int(record_id)

                        self.left_axis_ids.discard(context_id)
                        self.right_axis_ids.add(context_id)
                    elif record_type == 'modelingResult':
                        result_id = int(record_id)

                        self.left_axis_model_ids.discard(result_id)
                        self.right_axis_model_ids.add(result_id)
                    else:
                        raise ValueError(f"Unexpected record type: {record_type}")
                else:
                    raise ValueError(f"Unexpected axis: {value}")

            elif arg == 'log-left':
                self.log_left = True
            elif arg == 'log-right':
                self.log_right = True

            elif arg == 'cellCountUnits':
                self.cell_count_units = value
            elif arg == 'cfuCountUnits':
                self.cfu_count_units = value
            elif arg == 'metaboliteUnits':
                self.metabolite_units = value

    def get_measurements_df(self, measurement_context_ids):
        query = (
            sql.select(
                Measurement.contextId,
                Measurement.timeInHours.label("time"),
                Measurement.value,
                Measurement.std,
            )
            .select_from(Measurement)
            .where(
                Measurement.contextId.in_(measurement_context_ids),
                Measurement.value.is_not(None),
            )
            .order_by(Measurement.contextId, Measurement.timeInSeconds)
        )

        return execute_into_df(self.db_session, query)
