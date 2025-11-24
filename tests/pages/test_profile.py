import tests.init  # noqa: F401

from tests.page_test import PageTest
from app.model.lib.dev import bootstrap_study


class TestProfile(PageTest):
    def setUp(self):
        super().setUp()

        self._bootstrap_taxa()
        self._bootstrap_metabolites()

        # Log in:
        self.user = self.create_user(uuid='test_user')
        response = self.client.post('/backdoor/', data={'user_uuid': 'test_user'})
        self.assertEqual(response.status_code, 302)

    def test_claiming_a_project(self):
        s1 = bootstrap_study(self.db_session, 'synthetic_gut', 'test_user')
        s2 = bootstrap_study(self.db_session, 'ri_bt_bh_in_chemostat_controls', 'another_user')

        response = self.client.get('/profile/')
        response_text = self._get_text(response)

        self.assertEqual(response.status_code, 200)
        self.assertIn(f"[{s1.project.publicId}] Synthetic human gut bacterial community", response_text)
        self.assertNotIn(f"[{s2.project.publicId}] RI, BT and BH in chemostat", response_text)

        # Claim project successfully:
        response_text = self._claim_project(s2.project.uuid)

        self.assertIn(f"[{s1.project.publicId}] Synthetic human gut bacterial community", response_text)
        self.assertIn(f"[{s2.project.publicId}] RI, BT and BH in chemostat", response_text)

        # Can't claim a project twice
        response_text = self._claim_project(s2.project.uuid)
        self.assertIn("You already have access to this project", response_text)

        # Can't claim a nonexistent project:
        response_text = self._claim_project('nonexistent')
        self.assertIn("A project with this UUID couldn't be found", response_text)

    def test_claiming_a_study(self):
        s1 = bootstrap_study(self.db_session, 'synthetic_gut', 'test_user')
        s2 = bootstrap_study(self.db_session, 'ri_bt_bh_in_chemostat_controls', 'another_user')

        response = self.client.get('/profile/')
        response_text = self._get_text(response)

        self.assertEqual(response.status_code, 200)
        self.assertIn(f"[{s1.publicId}] Synthetic human gut bacterial community", response_text)
        self.assertNotIn(f"[{s2.publicId}] RI, BT and BH in chemostat: Controls", response_text)

        # Claim study successfully:
        response_text = self._claim_study(s2.uuid)

        self.assertIn(f"[{s1.publicId}] Synthetic human gut bacterial community", response_text)
        self.assertIn(f"[{s2.publicId}] RI, BT and BH in chemostat: Controls", response_text)

        # Can't claim a study twice
        response_text = self._claim_study(s2.uuid)

        self.assertIn("You already have access to this study", response_text)

        # Can't claim a nonexistent study:
        response_text = self._claim_study('nonexistent')

        self.assertIn("A study with this UUID couldn't be found", response_text)

    def _claim_project(self, uuid):
        response = self.client.post('/claim-project/', data={'uuid': uuid})
        self.assertEqual(response.status_code, 302)
        response = self.client.get('/profile/')
        return self._get_text(response)

    def _claim_study(self, uuid):
        response = self.client.post('/claim-study/', data={'uuid': uuid})
        self.assertEqual(response.status_code, 302)
        response = self.client.get('/profile/')
        return self._get_text(response)
