import plotly.express as px
import pandas as pd

from flask_app.lib.hack import get_chart_data

PLOTLY_TEMPLATE = 'plotly_white'


class ExperimentChartForm:
    @classmethod
    def from_df(cls, study_id, df):
        experiments = [e._asdict() for e in df.itertuples()]
        df_growth, df_reads = get_chart_data(study_id)

        return [cls(df_growth, df_reads, e) for e in experiments]

    def __init__(self, df_growth, df_reads, experiment):
        self.experiment_id    = experiment['experimentId']
        self.description      = experiment['experimentDescription']
        self.bioreplicate_ids = experiment['bioreplicateIds'].split(',')

        self.df_growth = df_growth
        self.df_reads = df_reads

        self.available_growth_measurements = [
            measurement
            for measurement in ['OD', 'Plate Counts', 'pH', 'FC']
            if measurement in df_growth.keys()
        ]

    def generate_growth_figures(self, measurement, args):
        df_growth, _ = self._filter_growth(args)

        fig = px.line(
            df_growth,
            x='Time',
            y=measurement,
            color='Biological_Replicate_id',
            title=f'{measurement} Plot for Experiment: {self.experiment_id} per Biological replicate',
            labels={'Time': 'Hours'},
            template=PLOTLY_TEMPLATE,
            markers=True
        )

        return [fig]

    def generate_reads_figures(self, args):
        df_reads, selected_bioreplicate_ids = self._filter_reads(args)

        figs = []
        for bioreplicate_id in selected_bioreplicate_ids:
            filtered_df = df_reads[df_reads['Biological_Replicate_id'] == bioreplicate_id]
            species_columns = filtered_df.filter(like='_counts').columns

            melted_df = filtered_df.melt(
                id_vars=['Time', 'Biological_Replicate_id'],
                value_vars=species_columns,
                var_name='Species',
                value_name='Cells/mL'
            )

            figs.append(px.line(
                melted_df,
                x='Time',
                y='Cells/mL',
                color='Species',
                title=f'FC Counts: {bioreplicate_id} per Microbial Strain',
                labels={'Time': 'Hours'},
                template=PLOTLY_TEMPLATE,
                markers=True
            ))

        return figs

    def generate_metabolite_figures(self, args):
        df_growth, selected_bioreplicate_ids = self._filter_growth(args)

        non_metabolite_keys = set([
            'Position', 'Biological_Replicate_id', 'Time',
            'OD', 'Plate Counts', 'pH', 'FC',
        ])
        metabolite_keys = set(df_growth.keys()).difference(non_metabolite_keys)

        figs = []
        for bioreplicate_id in selected_bioreplicate_ids:
            filtered_df = df_growth[df_growth['Biological_Replicate_id'] == bioreplicate_id]
            melted_df = filtered_df.melt(
                id_vars=['Time', 'Biological_Replicate_id'],
                value_vars=metabolite_keys,
                var_name='Metabolites',
                value_name='mM'
            )

            figs.append(px.line(
                melted_df,
                x='Time',
                y='mM',
                color='Metabolites',
                title=f'Metabolite Concentrations: {bioreplicate_id} per Metabolite',
                labels={'Time': 'Hours'},
                template=PLOTLY_TEMPLATE,
                markers=True
            ))

        return figs

    def _filter_growth(self, args):
        selected_bioreplicate_ids = []
        include_average = False

        for arg in args:
            if arg.endswith(':_average'):
                include_average = True
            elif arg.startswith('bioreplicate:'):
                selected_bioreplicate_ids.append(arg[len('bioreplicate:'):])

        filtered_data = self.df_growth[self.df_growth['Biological_Replicate_id'].isin(selected_bioreplicate_ids)]

        if include_average:
            numeric_cols = filtered_data.select_dtypes(include='number').columns.drop('Time')
            bioreplicate_label = f"Average {self.experiment_id}"

            experiment_data = self.df_growth[self.df_growth['Biological_Replicate_id'].isin(self.bioreplicate_ids)]
            mean_df_specific_ids = experiment_data.groupby('Time')[numeric_cols].mean().reset_index()
            mean_df_specific_ids['Biological_Replicate_id'] = bioreplicate_label

            filtered_data = pd.concat([filtered_data, mean_df_specific_ids], ignore_index=True)
            selected_bioreplicate_ids.append(bioreplicate_label)

        return filtered_data, selected_bioreplicate_ids

    def _filter_reads(self, args):
        columns_to_keep = [
            col
            for col in self.df_reads.columns
            if not col.endswith('_std') and col != 'Position'
        ]
        filtered_data = self.df_reads[columns_to_keep]

        selected_bioreplicate_ids = []
        include_average = False

        for arg in args:
            if arg.endswith(':_average'):
                include_average = True
            elif arg.startswith('bioreplicate:'):
                selected_bioreplicate_ids.append(arg[len('bioreplicate:'):])

        filtered_data = filtered_data[filtered_data['Biological_Replicate_id'].isin(selected_bioreplicate_ids)]

        if include_average:
            numeric_cols = filtered_data.select_dtypes(include='number').columns.drop('Time')
            bioreplicate_label = f"Average {self.experiment_id}"

            experiment_data = self.df_reads[self.df_reads['Biological_Replicate_id'].isin(self.bioreplicate_ids)]
            mean_df_specific_ids = experiment_data.groupby('Time')[numeric_cols].mean().reset_index()
            mean_df_specific_ids['Biological_Replicate_id'] = bioreplicate_label

            filtered_data = pd.concat([filtered_data, mean_df_specific_ids], ignore_index=True)
            selected_bioreplicate_ids.append(bioreplicate_label)

        return filtered_data, selected_bioreplicate_ids