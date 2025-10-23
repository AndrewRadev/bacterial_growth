import sqlalchemy as sql

from app.model.orm import (
    Bioreplicate,
    Compartment,
    Experiment,
    Measurement,
    MeasurementContext,
)
from app.model.lib.db import execute_into_df
from app.model.lib.conversion import (
    convert_df_units,
    CELL_COUNT_UNITS,
    CFU_COUNT_UNITS,
)


class ExperimentExportForm:
    def __init__(self, db_session, args):
        self.db_session = db_session

        self.bioreplicate_uuids = []
        self._extract_bioreplicate_args(args)

        self.csv_separator = ','
        self._extract_csv_args(args)

        self.cell_count_units = 'Cells/mL'
        self.cfu_count_units  = 'CFUs/mL'
        self.metabolite_units = 'mM'
        self._extract_measurement_unit_args(args)

        self.experiments = self.db_session.scalars(
            sql.select(Experiment)
            .join(Bioreplicate)
            .where(Bioreplicate.id.in_(self.bioreplicate_uuids))
            .group_by(Experiment.publicId)
            .order_by(Experiment.publicId)
        ).all()

    def get_experiment_data(self):
        experiment_data = {}

        for experiment in self.experiments:
            measurement_dfs = []
            measurement_targets = {
                'bioreplicate': set(),
                'metabolite':   set(),
                'strain':       set(),
            }

            # Collect targets for each column of measurements:
            for measurement_context in experiment.measurementContexts:
                if measurement_context.subjectType == 'bioreplicate':
                    measurement_targets['bioreplicate'].add(measurement_context.technique)
                else:
                    subject = measurement_context.get_subject(self.db_session)
                    measurement_targets[measurement_context.subjectType].add((
                        subject,
                        measurement_context.technique,
                    ))

            # Strain-level measurements:
            for (subject, technique) in sorted(measurement_targets['strain']):
                condition = (
                    MeasurementContext.subjectType == 'strain',
                    MeasurementContext.subjectId == subject.id,
                    MeasurementContext.techniqueId == technique.id,
                )

                query = self._base_bioreplicate_query(experiment).where(*condition)
                df = execute_into_df(self.db_session, query)

                if technique.units in CELL_COUNT_UNITS:
                    units = convert_df_units(df, technique.units, self.cell_count_units)
                elif technique.units in CFU_COUNT_UNITS:
                    units = convert_df_units(df, technique.units, self.cfu_count_units)
                else:
                    units = technique.units

                value_label = f"{subject.name} {technique.short_name} ({units})"

                df.rename(inplace=True, columns={'value': value_label})
                measurement_dfs.append(df)

            # Bioreplicate-level measurements:
            for technique in measurement_targets['bioreplicate']:
                condition = (
                    MeasurementContext.subjectType == 'bioreplicate',
                    MeasurementContext.techniqueId == technique.id,
                )

                query = self._base_bioreplicate_query(experiment).where(*condition)
                df = execute_into_df(self.db_session, query)

                if technique.units in CELL_COUNT_UNITS:
                    units = convert_df_units(df, technique.units, self.cell_count_units)
                elif technique.units in CFU_COUNT_UNITS:
                    units = convert_df_units(df, technique.units, self.cfu_count_units)
                else:
                    units = technique.units

                value_label = f"Community {technique.short_name}"
                if units is not None and units != '':
                    value_label += f" ({units})"

                df.rename(inplace=True, columns={'value': value_label})
                measurement_dfs.append(df)

            # Metabolite measurements:
            for (subject, technique) in sorted(measurement_targets['metabolite']):
                condition = (
                    MeasurementContext.subjectType == 'metabolite',
                    MeasurementContext.subjectId == subject.id,
                )

                query = self._base_bioreplicate_query(experiment).where(*condition)
                df = execute_into_df(self.db_session, query)

                units = convert_df_units(df, technique.units, self.metabolite_units, subject.averageMass)
                value_label = f"{subject.name} ({units})"

                df.rename(inplace=True, columns={'value': value_label})
                measurement_dfs.append(df)

            if len(measurement_dfs) == 0:
                continue

            # Join separate dataframes, one per column
            experiment_df = measurement_dfs[0]
            for df in measurement_dfs[1:]:
                experiment_df = experiment_df.merge(
                    df,
                    how='left',
                    on=['Time (hours)', 'Biological Replicate', 'Compartment'],
                    validate='one_to_one',
                    suffixes=(None, None),
                )

            if len(experiment_df) == 0:
                continue

            experiment_data[experiment] = experiment_df

        return experiment_data

    def _base_bioreplicate_query(self, experiment):
        return (
            sql.select(
                Measurement.timeInHours.label("Time (hours)"),
                Bioreplicate.name.label("Biological Replicate"),
                Compartment.name.label("Compartment"),
                Measurement.value.label("value"),
            )
            .select_from(Measurement)
            .join(MeasurementContext)
            .join(Bioreplicate)
            .join(Compartment)
            .join(Experiment)
            .where(
                Experiment.publicId == experiment.publicId,
                Bioreplicate.id.in_(self.bioreplicate_uuids),
            )
            .order_by(
                Bioreplicate.name,
                Compartment.name,
                Measurement.timeInSeconds,
            )
        )

    def _extract_bioreplicate_args(self, args):
        for arg in args.getlist('bioreplicates'):
            self.bioreplicate_uuids.append(arg)

    def _extract_csv_args(self, args):
        delimiter = args.get('delimiter', 'comma')

        if delimiter == 'comma':
            self.csv_separator = ','
        elif delimiter == 'tab':
            self.csv_separator = '\t'
        elif delimiter == 'custom':
            self.csv_separator = args.get('custom_delimiter', '|')
            if self.csv_separator == '':
                self.csv_separator = ' '
        else:
            raise Exception(f"Unknown delimiter requested: {delimiter}")

    def _extract_measurement_unit_args(self, args):
        self.cell_count_units = args.get('cellCountUnits', self.cell_count_units)
        self.cfu_count_units  = args.get('cfuCountUnits', self.cfu_count_units)
        self.metabolite_units = args.get('metaboliteUnits', self.metabolite_units)
