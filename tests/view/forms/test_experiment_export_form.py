import tests.init  # noqa: F401

import unittest
import math

import pandas as pd
from werkzeug.datastructures import MultiDict

from tests.database_test import DatabaseTest
from app.view.forms.experiment_export_form import ExperimentExportForm


class TestExperimentExportForm(DatabaseTest):
    def test_finding_experiments_based_on_given_bioreplicates(self):
        e1 = self.create_experiment()
        b1 = self.create_bioreplicate(experimentId=e1.publicId)
        b2 = self.create_bioreplicate(experimentId=e1.publicId)

        e2 = self.create_experiment()
        b3 = self.create_bioreplicate(experimentId=e2.publicId)
        b4 = self.create_bioreplicate(experimentId=e2.publicId)

        form = ExperimentExportForm(self.db_session, MultiDict([
            ('bioreplicates', b1.id),
            ('bioreplicates', b2.id),
        ]))
        self.assertEqual(form.experiments, [e1])

        form = ExperimentExportForm(self.db_session, MultiDict([
            ('bioreplicates', b3.id),
        ]))
        self.assertEqual(form.experiments, [e2])

        form = ExperimentExportForm(self.db_session, MultiDict([
            ('bioreplicates', b1.id),
            ('bioreplicates', b4.id),
        ]))
        self.assertEqual(form.experiments, [e1, e2])

    def test_fetching_experiment_data(self):
        e1 = self.create_experiment()
        b1 = self.create_bioreplicate(experimentId=e1.publicId)
        c1 = self.create_compartment(studyId=e1.study.publicId)

        self.create_experiment_compartment(compartmentId=c1.id, experimentId=e1.publicId)

        m1 = self.create_metabolite(name='glucose', averageMass=7)
        self.create_study_metabolite(chebiId=m1.chebiId, studyId=e1.study.publicId)

        s1 = self.create_strain(name="Roseburia", studyId=e1.study.publicId)

        targets = [
            ('bioreplicate', b1, 'od',         'CFUs/μL'),
            ('bioreplicate', b1, 'ph',         ''),
            ('metabolite',   m1, 'Metabolite', 'g/L'),
            ('strain',       s1, 'fc',         'Cells/μL'),
        ]

        for subject_type, subject, technique_type, units in targets:
            technique = self.create_measurement_technique(
                type=technique_type,
                units=units,
            )

            mc = self.create_measurement_context(
                bioreplicateId=b1.id,
                compartmentId=c1.id,
                subjectId=subject.id,
                techniqueId=technique.id,
                subjectType=subject_type,
            )
            for i, v in enumerate(range(1, 10)):
                self.create_measurement(
                    timeInSeconds=(i * 3600),
                    value=v,
                    contextId=mc.id,
                    studyId=e1.study.publicId,
                )

        form = ExperimentExportForm(self.db_session, MultiDict([('bioreplicates', b1.id)]))
        data = form.get_experiment_data()

        self.assertTrue(e1 in data)
        self.assertEqual(
            sorted(data[e1].columns.tolist()),
            sorted([
                'Time (hours)',
                'Biological Replicate',
                'Compartment',
                'Roseburia FC (Cells/mL)',
                'Community OD (CFUs/mL)',
                'Community pH',
                'glucose (mM)',
            ]),
        )
        self.assertEqual(data[e1].shape[0], 9)

    def test_merging_experiment_data_with_different_timepoints(self):
        e1 = self.create_experiment()
        b1 = self.create_bioreplicate(experimentId=e1.publicId)
        c1 = self.create_compartment(studyId=e1.study.publicId)

        self.create_experiment_compartment(compartmentId=c1.id, experimentId=e1.publicId)

        # OD measured at t = 0, 10, 20
        t1 = self.create_measurement_technique(type='od')
        mc1 = self.create_measurement_context(
            bioreplicateId=b1.id,
            compartmentId=c1.id,
            subjectId=b1.id,
            techniqueId=t1.id,
            subjectType='bioreplicate'
        )
        for i in [0, 10, 20]:
            self.create_measurement(
                timeInSeconds=(i * 3600),
                value=i * 10,
                contextId=mc1.id,
                studyId=e1.study.publicId,
            )

        # pH measured at t = 0, 8, 24
        t2 = self.create_measurement_technique(type='ph')
        mc2 = self.create_measurement_context(
            bioreplicateId=b1.id,
            compartmentId=c1.id,
            subjectId=b1.id,
            techniqueId=t2.id,
            subjectType='bioreplicate'
        )
        for i in [0, 8, 24]:
            self.create_measurement(
                timeInSeconds=(i * 3600),
                value=i * 10,
                contextId=mc2.id,
                studyId=e1.study.publicId,
            )

        form = ExperimentExportForm(self.db_session, MultiDict([('bioreplicates', b1.id)]))
        e1_data = form.get_experiment_data()[e1].replace({math.nan: None})

        self.assertEqual(e1_data['Time (hours)'].tolist(), [0, 8, 10, 20, 24])
        self.assertEqual(e1_data['Community OD'].tolist(), [0.0, None, 100.0, 200.0, None])
        self.assertEqual(e1_data['Community pH'].tolist(), [0.0, 80.0, None, None, 240.0])


if __name__ == '__main__':
    unittest.main()
