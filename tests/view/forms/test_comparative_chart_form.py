import tests.init  # noqa: F401

import unittest
import math

import pandas as pd
from werkzeug.datastructures import MultiDict

from tests.database_test import DatabaseTest
from app.view.forms.comparative_chart_form import ComparativeChartForm


class TestExperimentExportForm(DatabaseTest):
    def test_permalink_query(self):
        s = self.create_study()
        t = self.create_measurement_technique()

        e1 = self.create_experiment(studyId=s.publicId)
        b1 = self.create_bioreplicate(experimentId=e1.publicId)
        mc1 = self.create_measurement_context(bioreplicateId=b1.id, techniqueId=t.id)
        mr1 = self.create_modeling_result(measurementContextId=mc1.id, type='custom_1')
        for i in range(3):
            self.create_measurement(timeInSeconds=i, value=i, contextId=mc1.id)

        e2 = self.create_experiment(studyId=s.publicId)
        b2 = self.create_bioreplicate(experimentId=e2.publicId)
        mc2 = self.create_measurement_context(bioreplicateId=b2.id, techniqueId=t.id)
        mr2 = self.create_modeling_result(measurementContextId=mc2.id, type='custom_1')
        for i in range(3):
            self.create_measurement(timeInSeconds=i, value=i, contextId=mc2.id)

        # Parameters joined with commas:
        form = ComparativeChartForm(
            self.db_session,
            left_axis_ids=[mc1.id, mc2.id],
            left_axis_model_ids=[mr1.id, mr2.id],
        )
        form.build_chart()
        self.assertEqual(
            form.permalink_query,
            f"l={mc1.id},{mc2.id}&lm={mr1.id},{mr2.id}&selectedExperimentId={e1.publicId}&selectedTechniqueId={t.id}",
        )

        # Full set of parameters:
        form = ComparativeChartForm(
            self.db_session,
            left_axis_ids=[mc2.id],
            right_axis_ids=[mc1.id],
            left_axis_model_ids=[mr1.id],
            right_axis_model_ids=[mr2.id],
        )
        form.build_chart()
        self.assertEqual(
            form.permalink_query,
            f"l={mc2.id}&r={mc1.id}&lm={mr1.id}&rm={mr2.id}&selectedExperimentId={e1.publicId}&selectedTechniqueId={t.id}",
        )

        # First experiment from measurements is picked as the one to redirect to:
        form = ComparativeChartForm(
            self.db_session,
            left_axis_ids=[mc2.id],
            left_axis_model_ids=[mr1.id],
        )
        form.build_chart()
        self.assertEqual(
            form.permalink_query,
            f"l={mc2.id}&lm={mr1.id}&selectedExperimentId={e2.publicId}&selectedTechniqueId={t.id}",
        )


if __name__ == '__main__':
    unittest.main()
