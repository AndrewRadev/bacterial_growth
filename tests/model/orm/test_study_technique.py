import tests.init  # noqa: F401

import unittest

from app.model.orm import StudyTechnique
from tests.database_test import DatabaseTest

class TestStudyTechnique(DatabaseTest):
    def test_name_descriptions(self):
        st = StudyTechnique(type='od', subjectType='bioreplicate')

        self.assertEqual(st.long_name, 'Optical Density')
        self.assertEqual(st.long_name_with_subject_type, 'Optical Density per community')

        st.type = 'fc'

        self.assertEqual(st.long_name, 'Flow Cytometry')
        self.assertEqual(st.long_name_with_subject_type, 'Flow Cytometry per community')

        st.subjectType = 'strain'
        st.label = 'using 16s'

        self.assertEqual(st.long_name, 'Flow Cytometry')
        self.assertEqual(st.long_name_with_subject_type, 'Flow Cytometry per strain (using 16s)')

        st.type = 'metabolite'
        st.subjectType = 'metabolite'
        st.label = None

        self.assertEqual(st.long_name, 'Metabolites')
        self.assertEqual(st.long_name_with_subject_type, 'Metabolites')

        st.label = 'AUC'

        self.assertEqual(st.long_name, 'Metabolites')
        self.assertEqual(st.long_name_with_subject_type, 'Metabolites (AUC)')


if __name__ == '__main__':
    unittest.main()
