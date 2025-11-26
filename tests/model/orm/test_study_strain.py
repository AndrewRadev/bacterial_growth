import tests.init  # noqa: F401

import unittest

from app.model.orm import StudyStrain
from tests.database_test import DatabaseTest


class TestStudyStrain(DatabaseTest):
    def test_search_basic(self):
        self.create_study_strain(taxon=dict(ncbiId="1", name="Vibrio pelagius"))
        self.create_study_strain(taxon=dict(ncbiId="2", name="Anaerovibrio"))
        self.create_study_strain(taxon=dict(ncbiId="3", name="Brevibacterium linens"))

        # Results only consider the prefix
        results, _ = StudyStrain.search_by_name(self.db_session, 'Vibrio')
        self.assertEqual(
            ['Vibrio pelagius (NCBI:1)'],
            [r['text'] for r in results]
        )

        # Matches are case-insensitive:
        results, _ = StudyStrain.search_by_name(self.db_session, 'Vib')
        self.assertEqual(
            sorted(['Vibrio pelagius (NCBI:1)']),
            sorted([r['text'] for r in results])
        )

        # All records are returned by default
        all_records = sorted([
            'Vibrio pelagius (NCBI:1)',
            'Anaerovibrio (NCBI:2)',
            'Brevibacterium linens (NCBI:3)',
        ])

        results, _ = StudyStrain.search_by_name(self.db_session, '')
        self.assertEqual(all_records, [r['text'] for r in results])

        results, _ = StudyStrain.search_by_name(self.db_session, ' ')
        self.assertEqual(all_records, [r['text'] for r in results])

    def test_search_by_multiple_words(self):
        self.create_study_strain(taxon=dict(ncbiId="1", name="Salmonella enterica serovar Infantis"))
        self.create_study_strain(taxon=dict(ncbiId="2", name="Salmonella enterica serovar Moscow"))

        # Words are searched separately:
        results, _ = StudyStrain.search_by_name(self.db_session, 'salmonella infantis')
        self.assertEqual(
            ['Salmonella enterica serovar Infantis (NCBI:1)'],
            [r['text'] for r in results]
        )

        # Words are searched in order:
        results, _ = StudyStrain.search_by_name(self.db_session, 'infantis salmonella')
        self.assertEqual(
            [],
            [r['text'] for r in results]
        )

    def test_pagination(self):
        self.create_study_strain(taxon=dict(name="Test 1 foo"))
        self.create_study_strain(taxon=dict(name="Test 2 foo"))
        self.create_study_strain(taxon=dict(name="Test 3 bar"))
        self.create_study_strain(taxon=dict(name="Test 4 bar"))

        # Two per page, two pages:
        results, has_more = StudyStrain.search_by_name(self.db_session, 'Test', page=1, per_page=2)
        self.assertEqual(len(results), 2)
        self.assertTrue(has_more)

        results, has_more = StudyStrain.search_by_name(self.db_session, 'Test', page=2, per_page=2)
        self.assertEqual(len(results), 2)
        self.assertFalse(has_more)

        # Three per page, two pages:
        results, has_more = StudyStrain.search_by_name(self.db_session, 'Test', page=1, per_page=3)
        self.assertEqual(len(results), 3)
        self.assertTrue(has_more)

        results, has_more = StudyStrain.search_by_name(self.db_session, 'Test', page=2, per_page=3)
        self.assertEqual(len(results), 1)
        self.assertFalse(has_more)

        # Page ten, no results:
        results, has_more = StudyStrain.search_by_name(self.db_session, 'Test', page=10, per_page=3)
        self.assertEqual(len(results), 0)
        self.assertFalse(has_more)

        # Pagination correctly takes into account two-word searches:
        results, has_more = StudyStrain.search_by_name(self.db_session, 'Test foo', page=1, per_page=1)
        self.assertEqual(len(results), 1)
        self.assertTrue(has_more)


if __name__ == '__main__':
    unittest.main()
