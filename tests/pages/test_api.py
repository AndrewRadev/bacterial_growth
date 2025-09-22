import tests.init  # noqa: F401

from datetime import datetime, UTC

from tests.page_test import PageTest


class TestApiPages(PageTest):
    def test_project_json(self):
        project = self.create_project(name='Example project')
        s1 = self.create_study(projectUuid=project.uuid)
        s2 = self.create_study(projectUuid=project.uuid)

        self.db_session.commit()

        response = self.client.get(f"/api/v1/project/{project.publicId}.json")
        response_json = self._get_json(response)

        self.assertEqual(response_json['id'], project.publicId)
        self.assertEqual(response_json['name'], 'Example project')
        self.assertEqual([s['id'] for s in response_json['studies']], [s1.publicId, s2.publicId])

        # Nonexisting project:
        response = self.client.get(f"/api/v1/project/nonexisting.json")
        response_json = self._get_json(response)

        self.assertEqual(response_json['error'], '404 Not found')

    def test_published_study_json(self):
        study = self.create_study(name='Example study', publishedAt=datetime.now(UTC))
        e1    = self.create_experiment(studyId=study.publicId)
        e2    = self.create_experiment(studyId=study.publicId)

        self.db_session.commit()

        response = self.client.get(f"/api/v1/study/{study.publicId}.json")
        response_json = self._get_json(response)

        self.assertEqual(response_json['id'], study.publicId)
        self.assertEqual(response_json['name'], 'Example study')
        self.assertEqual([e['id'] for e in response_json['experiments']], [e1.publicId, e2.publicId])

    def test_nonexistent_study(self):
        response = self.client.get('/api/v1/study/nonexisting.json')
        response_json = self._get_json(response)

        self.assertEqual(response_json['error'], '404 Not found')

    def test_non_published_study(self):
        study = self.create_study(name='Example study', publishedAt=None)
        e1 = self.create_experiment(studyId=study.publicId)
        self.db_session.commit()

        response = self.client.get(f"/api/v1/study/{study.publicId}.json")
        response_json = self._get_json(response)

        # Study is visible, but limited data is returned
        self.assertEqual(response_json['id'], study.publicId)
        self.assertEqual(set(response_json.keys()), {'id', 'name', 'projectId'})

    def test_published_experiment_json(self):
        study        = self.create_study(publishedAt=datetime.now(UTC))
        experiment   = self.create_experiment(name='Example experiment', studyId=study.publicId)
        bioreplicate = self.create_bioreplicate(experimentId=experiment.publicId)

        self.create_measurement_context(
            bioreplicateId=bioreplicate.id,
            subjectId=bioreplicate.id,
            subjectType='bioreplicate',
        )
        self.create_measurement_context(
            bioreplicateId=bioreplicate.id,
            subjectId=self.create_strain(name='Roseburia').id,
            subjectType='strain',
        )
        self.create_measurement_context(
            bioreplicateId=bioreplicate.id,
            subjectId=self.create_metabolite(name='glucose').id,
            subjectType='metabolite',
        )

        self.db_session.commit()

        response = self.client.get(f"/api/v1/experiment/{experiment.publicId}.json")
        response_json = self._get_json(response)

        self.assertEqual(response_json['id'], experiment.publicId)
        self.assertEqual(response_json['name'], 'Example experiment')

        self.assertEqual(len(response_json['bioreplicates']), 1)
        self.assertEqual(len(response_json['bioreplicates'][0]['measurementContexts']), 3)

    def test_nonexisting_experiment(self):
        response = self.client.get('/api/v1/experiment/nonexisting.json')
        response_json = self._get_json(response)

        self.assertEqual(response_json['error'], '404 Not found')

    def test_non_published_experiment(self):
        study      = self.create_study(publishedAt=None)
        experiment = self.create_experiment(name='Example experiment', studyId=study.publicId)
        self.db_session.commit()

        response = self.client.get(f"/api/v1/experiment/{experiment.publicId}.json")
        response_json = self._get_json(response)

        self.assertEqual(response_json['error'], '404 Not found')
