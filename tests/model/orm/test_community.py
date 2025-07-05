import tests.init  # noqa: F401

import unittest

from app.model.orm import Community
from tests.database_test import DatabaseTest


class TestCommunity(DatabaseTest):
    def test_successful_creation(self):
        study = self.create_study()
        strain1 = self.create_strain(studyId=study.publicId)
        strain2 = self.create_strain(studyId=study.publicId)

        community = Community(studyId=study.publicId, name="Test community")
        self.db_session.add(community)
        self.db_session.flush()

        self.create_community_strain(communityId=community.id, strainId=strain1.id)
        self.create_community_strain(communityId=community.id, strainId=strain2.id)
        self.db_session.refresh(community)

        self.assertIsNotNone(community.id)
        self.assertEqual(community.strains, [strain1, strain2])

    def test_describe_differences(self):
        strain1 = self.create_strain(name="Roseburia")
        strain2 = self.create_strain(name="Blautia")
        strain3 = self.create_strain(name="Bacteroides")

        c1 = self.create_community()
        c2 = self.create_community()

        c1.strains = [strain1, strain2]
        c2.strains = [strain2, strain3]

        diff = c1.diff(c2)
        self.assertEqual(diff['removed'], {strain1})
        self.assertEqual(diff['added'], {strain3})

        diff = c2.diff(c1)
        self.assertEqual(diff['added'], {strain1})
        self.assertEqual(diff['removed'], {strain3})


if __name__ == '__main__':
    unittest.main()
