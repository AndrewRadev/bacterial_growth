import zipfile
from io import BytesIO

from flask import render_template, send_file, request

import models.study_dfs as study_dfs
from models.experiment_df_wrapper import ExperimentDfWrapper

from legacy.chart_data import get_chart_data
from db import get_connection


def study_show_page(studyId):
    with get_connection() as conn:
        study = study_dfs.get_general_info(studyId, conn)

        study['experiments']               = study_dfs.get_experiments(studyId, conn)
        study['compartments']              = study_dfs.get_compartments(studyId, conn)
        study['communities']               = study_dfs.get_communities(studyId, conn)
        study['microbial_strains']         = study_dfs.get_microbial_strains(studyId, conn)
        study['biological_replicates']     = study_dfs.get_biological_replicates(studyId, conn)
        study['abundances']                = study_dfs.get_abundances(studyId, conn)
        study['fc_counts']                 = study_dfs.get_fc_counts(studyId, conn)
        study['metabolites_per_replicate'] = study_dfs.get_metabolites_per_replicate(studyId, conn)

        return render_template("pages/studies/show.html", study=study)


def study_export_page(studyId):
    with get_connection() as conn:
        study = study_dfs.get_general_info(studyId, conn)

        study['experiments']           = study_dfs.get_experiments(studyId, conn)
        study['biological_replicates'] = study_dfs.get_biological_replicates(studyId, conn)

        return render_template("pages/studies/export.html", study=study, studyId=studyId)


def study_export_preview_fragment(studyId):
    sep = extract_csv_separator(request.args)

    with get_connection() as conn:
        csv_previews = []
        selected_bioreplicate_ids = request.args.getlist('bioreplicates')

        for experiment in get_experiment_data_for_export(studyId, conn, selected_bioreplicate_ids):
            if len(experiment.df) == 0:
                continue

            csv = experiment.df[:5].to_csv(index=False, sep=sep)
            csv_previews.append(f"""
                <h3>{experiment.experiment_id}.csv ({len(experiment.df)} rows)</h3>
                <pre>{csv}</pre>
            """)

        return '\n'.join(csv_previews)


def study_download_zip(studyId):
    sep = extract_csv_separator(request.args)

    with get_connection() as conn:
        csv_data = []
        selected_bioreplicate_ids = request.args.getlist('bioreplicates')
        experiments = get_experiment_data_for_export(studyId, conn, selected_bioreplicate_ids)

        for experiment in experiments:
            if len(experiment.df) == 0:
                continue

            csv_bytes = experiment.df.to_csv(index=False, sep=sep)
            csv_name = f"{experiment.experiment_id}.csv"

            csv_data.append((csv_name, csv_bytes))

        study = study_dfs.get_general_info(studyId, conn)
        readme_text = render_template('pages/studies/export_readme.md', study=study, experiments=experiments)

    zip_file = createzip(csv_data, readme_text)

    return send_file(
        zip_file,
        as_attachment=True,
        download_name=f"{studyId}.zip",
    )


def extract_csv_separator(args):
    delimiter = args.get('delimiter', 'comma')

    if delimiter == 'comma':
        sep = ','
    elif delimiter == 'tab':
        sep = '\t'
    elif delimiter == 'custom':
        sep = args.get('custom_delimiter', '|')
        if sep == '':
            sep = ' '
    else:
        raise Exception(f"Unknown delimiter requested: {delimiter}")

    return sep


def get_experiment_data_for_export(studyId, conn, selected_bioreplicate_ids):
    df_growth, df_reads = get_chart_data(studyId)

    experiments = study_dfs.get_experiments(studyId, conn)
    bioreps     = study_dfs.get_biological_replicates(studyId, conn)

    filtered_experiments = []

    for experimentId, description in zip(experiments['experimentId'], experiments['experimentDescription']):
        # Filter data by the requested bioreplicates:
        bioreplicate_ids = bioreps[bioreps['experimentId'] == experimentId]['bioreplicateId']

        available_bioreplicate_ids = set((*bioreplicate_ids, f"Average {experimentId}"))
        target_bioreplicate_ids = set(selected_bioreplicate_ids).intersection(available_bioreplicate_ids)

        # Work on growth data:
        experiment_growth = ExperimentDfWrapper(df_growth, experimentId, bioreplicate_ids, description)
        experiment_growth.select_bioreplicates(target_bioreplicate_ids)
        experiment_growth.drop_columns('Position')

        # Reorder columns:
        growth_measurement_columns = experiment_growth.get_measurement_keys()
        metabolite_columns         = experiment_growth.get_metabolite_keys()

        # Work on reads:
        experiment_reads = ExperimentDfWrapper(df_reads, experimentId, bioreplicate_ids, description)
        experiment_reads.select_bioreplicates(target_bioreplicate_ids)
        experiment_reads.drop_columns('Position')

        reads_columns = [c for c in experiment_reads.keys() if c.endswith(('_reads', '_counts'))]

        # We ignore std measurements for the export
        for column in experiment_reads.keys():
            if column.endswith('_std'):
                experiment_reads.drop_columns(column)

        experiment = experiment_growth.merge(experiment_reads)

        def relabel_columns(column):
            if column == 'Time':
                return f"{column} (hours)"
            elif column == 'Biological_Replicate_id':
                # Tidy up the name for readability:
                return "Biological Replicate ID"
            elif column == 'FC':
                return f"{column} (Cells/mL)"
            elif column in metabolite_columns:
                return f"{column} (mM)"
            elif column.endswith('_reads'):
                return f"{column.removesuffix('_reads')} reads"
            elif column.endswith('_counts'):
                return f"{column.removesuffix('_counts')} counts"
            else:
                return column

        experiment.reorder_columns([
            'Time', 'Biological_Replicate_id',
            *sorted(reads_columns),
            *growth_measurement_columns,
            *sorted(metabolite_columns)
        ])

        experiment.rename_columns(relabel_columns)

        filtered_experiments.append(experiment)

    return filtered_experiments


def createzip(csv_data: list[tuple[str, bytes]], readme_text: str):
    buf = BytesIO()

    with zipfile.ZipFile(buf, 'w', zipfile.ZIP_DEFLATED) as csv_zip:
        for (csv_name, csv_bytes) in csv_data:
            csv_zip.writestr(csv_name, csv_bytes)

        csv_zip.writestr('README.md', readme_text)

    buf.seek(0)
    return buf
