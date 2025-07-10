import tests.init  # noqa: F401

import unittest

from tests.page_test import PageTest


class TestPerturbation(PageTest):
    def setUp(self):
        super().setUp()

        user = self.create_user(isAdmin=True)
        self._log_in(user)

    def test_compartment_changes(self):
        c1 = self.create_compartment(name="C1", initialPh=7, initialTemperature=37)
        c2 = self.create_compartment(name="C2", initialPh=3, initialTemperature=37)
        c3 = self.create_compartment(name="C3", initialPh=8, initialTemperature=40)

        # Removed compartment:
        p = self.create_perturbation(removedCompartmentId=c1.id)
        self.db_session.commit()

        response = self.client.get(f"/perturbation/{p.id}")
        response_text = self._get_text(response)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Compartment C1 removed", response_text)

        # Added compartment:
        p = self.create_perturbation(addedCompartmentId=c2.id)
        self.db_session.commit()

        response = self.client.get(f"/perturbation/{p.id}")
        response_text = self._get_text(response)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Compartment C2 added", response_text)

        # Replaced compartment:
        p = self.create_perturbation(removedCompartmentId=c1.id, addedCompartmentId=c3.id)
        self.db_session.commit()

        response = self.client.get(f"/perturbation/{p.id}")
        response_text = self._get_text(response)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Compartment C1 changed to C3", response_text)
        self.assertIn("initial pH : from 7.00 to 8.00", response_text)
        self.assertIn("initial temperature : from 37.00 to 40.00", response_text)

    def test_community_changes(self):
        s1 = self.create_strain(name="Blautia")
        s2 = self.create_strain(name="Roseburia")
        s3 = self.create_strain(name="Bacteroides")

        c1 = self.create_community(name="C1")
        self.create_community_strain(communityId=c1.id, strainId=s1.id)
        self.create_community_strain(communityId=c1.id, strainId=s2.id)

        c2 = self.create_community(name="C2")
        self.create_community_strain(communityId=c2.id, strainId=s2.id)
        self.create_community_strain(communityId=c2.id, strainId=s3.id)

        # Removed community:
        p = self.create_perturbation(oldCommunityId=c1.id)
        self.db_session.commit()

        response = self.client.get(f"/perturbation/{p.id}")
        response_text = self._get_text(response)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Community C1 removed", response_text)

        # Added community:
        p = self.create_perturbation(newCommunityId=c2.id)
        self.db_session.commit()

        response = self.client.get(f"/perturbation/{p.id}")
        response_text = self._get_text(response)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Community C2 added", response_text)

        # Replaced community:
        p = self.create_perturbation(oldCommunityId=c1.id, newCommunityId=c2.id)
        self.db_session.commit()

        response = self.client.get(f"/perturbation/{p.id}")
        response_text = self._get_text(response)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Community C1 changed to C2", response_text)
        self.assertIn("Strains added: Bacteroides", response_text)
        self.assertIn("Strains removed: Blautia", response_text)


if __name__ == '__main__':
    unittest.main()
