import tests.init  # noqa: F401

import unittest
from datetime import datetime, UTC

from app.model.lib.study_search import StudySearch
from tests.database_test import DatabaseTest

class TestStudySearch(DatabaseTest):
    def test_no_query(self):
        user1 = self.create_user()
        user2 = self.create_user()
        admin = self.create_user(isAdmin=True)

        s1 = self.create_study(name="Test study 1", publishedAt=datetime.now(UTC))
        s2 = self.create_study(name="Test study 2", publishedAt=datetime.now(UTC))

        # Not published, won't show up if there is no user:
        s3 = self.create_study(name="Test study 3", publishedAt=None)
        self.create_study_user(studyUniqueID=s3.uuid, userUniqueID=user2.uuid)

        # Owned by a particular user:
        s4 = self.create_study(name="Test study 4", publishedAt=None, ownerUuid=user1.uuid)

        search = StudySearch(self.db_session)
        self._assertEqualPublicIds(search.fetch_results(), [s2, s1])

        # Study shows up for its owner:
        search = StudySearch(self.db_session, user=user1)
        self._assertEqualPublicIds(search.fetch_results(), [s4, s2, s1])

        # Study shows up for a connected user:
        search = StudySearch(self.db_session, user=user2)
        self._assertEqualPublicIds(search.fetch_results(), [s3, s2, s1])

        # All studies show up for an admin
        search = StudySearch(self.db_session, user=admin)
        self._assertEqualPublicIds(search.fetch_results(), [s4, s3, s2, s1])

    def test_text_query(self):
        admin = self.create_user(isAdmin=True)

        s1 = self.create_study(name="Foo")
        s2 = self.create_study(name="Bar")
        s3 = self.create_study(name="FooBar")
        s4 = self.create_study(name="Test", description="Bar")

        search = StudySearch(self.db_session, user=admin, query="foo")
        self._assertEqualPublicIds(search.fetch_results(), [s3, s1])

        search = StudySearch(self.db_session, user=admin, query="BAR")
        self._assertEqualPublicIds(search.fetch_results(), [s4, s3, s2])

        search = StudySearch(self.db_session, user=admin, query="foobar")
        self._assertEqualPublicIds(search.fetch_results(), [s3])

    def test_public_id_query(self):
        admin = self.create_user(isAdmin=True)

        s1  = self.create_study(publicId="SMGDB00000001")
        s2  = self.create_study(publicId="SMGDB00000002")
        s30 = self.create_study(publicId="SMGDB00000030")

        search = StudySearch(self.db_session, user=admin, query="SMGDB00000001")
        self._assertEqualPublicIds(search.fetch_results(), [s1])

        search = StudySearch(self.db_session, user=admin, query="smgdb2")
        self._assertEqualPublicIds(search.fetch_results(), [s2])

        search = StudySearch(self.db_session, user=admin, query="SMGDB30")
        self._assertEqualPublicIds(search.fetch_results(), [s30])

        search = StudySearch(self.db_session, user=admin, query="smgdb000000000000000001")
        self._assertEqualPublicIds(search.fetch_results(), [s1])

    def test_strain_query(self):
        admin = self.create_user(isAdmin=True)

        roseburia = self.create_taxon(name="Roseburia")
        blautia   = self.create_taxon(name="Blautia")

        s1 = self.create_study()
        self.create_study_strain(studyId=s1.publicId, ncbiId=roseburia.ncbiId)

        s2 = self.create_study()
        self.create_study_strain(studyId=s2.publicId, ncbiId=blautia.ncbiId)

        s3 = self.create_study()
        self.create_study_strain(studyId=s3.publicId, ncbiId=roseburia.ncbiId)
        self.create_study_strain(studyId=s3.publicId, ncbiId=blautia.ncbiId)

        # No connected strains:
        s4 = self.create_study()

        search = StudySearch(self.db_session, user=admin, ncbiIds=[roseburia.ncbiId])
        self._assertEqualPublicIds(search.fetch_results(), [s3, s1])

        search = StudySearch(self.db_session, user=admin, ncbiIds=[blautia.ncbiId])
        self._assertEqualPublicIds(search.fetch_results(), [s3, s2])

        # TODO (2025-11-26) AND query for strains
        # search = StudySearch(self.db_session, user=admin, ncbiIds=[roseburia.ncbiId, blautia.ncbiId])
        # self._assertEqualPublicIds(search.fetch_results(), [s3])

    def _assertEqualPublicIds(self, list1, list2):
        get_public_id = lambda s: s.publicId
        self.assertEqual(
            list(map(get_public_id, list1)),
            list(map(get_public_id, list2)),
        )


if __name__ == '__main__':
    unittest.main()
