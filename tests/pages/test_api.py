import tests.init  # noqa: F401

from tests.page_test import PageTest


class TestApiPages(PageTest):
    def test_project_json(self):
        project = self.create_project(name='Example project')
        self.db_session.commit()

        response = self.client.get(f"/api/v1/project/{project.publicId}.json")
        response_json = self._get_json(response)

        self.assertEqual(response_json['id'], project.publicId)
        self.assertEqual(response_json['name'], 'Example project')

        # Nonexisting project:
        response = self.client.get(f"/api/v1/project/nonexisting.json")
        response_json = self._get_json(response)

        self.assertEqual(response_json['error'], '404 Not found')

    def test_study_json(self):
        study = self.create_study(name='Example study')
        self.db_session.commit()

        response = self.client.get(f"/api/v1/study/{study.publicId}.json")
        response_json = self._get_json(response)

        self.assertEqual(response_json['id'], study.publicId)
        self.assertEqual(response_json['name'], 'Example study')

        # Nonexisting study:
        response = self.client.get(f"/api/v1/study/nonexisting.json")
        response_json = self._get_json(response)

        self.assertEqual(response_json['error'], '404 Not found')

    def test_experiment_json(self):
        experiment = self.create_experiment(name='Example experiment')
        self.db_session.commit()

        response = self.client.get(f"/api/v1/experiment/{experiment.publicId}.json")
        response_json = self._get_json(response)

        self.assertEqual(response_json['id'], experiment.publicId)
        self.assertEqual(response_json['name'], 'Example experiment')

        # Nonexisting experiment:
        response = self.client.get(f"/api/v1/experiment/nonexisting.json")
        response_json = self._get_json(response)

        self.assertEqual(response_json['error'], '404 Not found')
