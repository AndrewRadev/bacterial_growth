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

        self.assertEqual(response.status, '404 NOT FOUND')
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
        study = self.create_study(publishedAt=datetime.now(UTC))

        # Create community for the experiment:
        community = self.create_community(studyId=study.publicId)
        self.create_community_strain(communityId=community.id)
        self.create_community_strain(communityId=community.id)

        # Create experiment:
        experiment = self.create_experiment(name='Example experiment', studyId=study.publicId, communityId=community.id)

        # Add compartments:
        compartment = self.create_compartment(studyId=study.publicId)
        self.create_experiment_compartment(experimentId=experiment.publicId, compartmentId=compartment.id)

        # Add 1 bioreplicate with 3 measurement contexts:
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

        self.assertEqual(len(response_json['communityStrains']), 2)

        self.assertEqual(len(response_json['bioreplicates']), 1)
        self.assertEqual(len(response_json['bioreplicates'][0]['measurementContexts']), 3)

    def test_nonexisting_experiment(self):
        response = self.client.get('/api/v1/experiment/nonexisting.json')
        response_json = self._get_json(response)

        self.assertEqual(response.status, '404 NOT FOUND')
        self.assertEqual(response_json['error'], '404 Not found')

    def test_non_published_experiment(self):
        study      = self.create_study(publishedAt=None)
        experiment = self.create_experiment(name='Example experiment', studyId=study.publicId)
        self.db_session.commit()

        response = self.client.get(f"/api/v1/experiment/{experiment.publicId}.json")
        response_json = self._get_json(response)

        self.assertEqual(response_json['error'], '404 Not found')

    def test_measurement_csv(self):
        study        = self.create_study(publishedAt=datetime.now(UTC))
        experiment   = self.create_experiment(studyId=study.publicId)
        bioreplicate = self.create_bioreplicate(experimentId=experiment.publicId)

        measurement_context = self.create_measurement_context(
            studyId=study.publicId,
            bioreplicateId=bioreplicate.id,
            subjectId=bioreplicate.id,
            subjectType='bioreplicate',
        )
        for i in range(1, 4):
            self.create_measurement(
                contextId=measurement_context.id,
                timeInSeconds=(i * 3600),
                value=(i * 10),
            )

        self.db_session.commit()

        response = self.client.get(f"/api/v1/measurement-context/{measurement_context.id}.csv")
        self.assertEqual(response.status, '200 OK')

        response_df = self._get_csv(response)

        self.assertEqual(response_df.columns.tolist(), ['time', 'value', 'std'])
        self.assertEqual(response_df['time'].tolist(), [1, 2, 3])
        self.assertEqual(response_df['value'].tolist(), [10, 20, 30])
        self.assertTrue(response_df['std'].isna().all())

    def test_non_published_measurement_csv(self):
        study        = self.create_study(publishedAt=None)
        experiment   = self.create_experiment(studyId=study.publicId)
        bioreplicate = self.create_bioreplicate(experimentId=experiment.publicId)

        measurement_context = self.create_measurement_context(
            bioreplicateId=bioreplicate.id,
            subjectId=bioreplicate.id,
            subjectType='bioreplicate',
        )
        self.create_measurement(
            contextId=measurement_context.id,
            timeInSeconds=3600,
            value=10,
        )

        self.db_session.commit()

        response = self.client.get(f"/api/v1/measurement-context/{measurement_context.id}.csv")

        # No data is returned for an unpublished experiment
        self.assertEqual(response.status, '404 NOT FOUND')
        self.assertEqual(response.data, b'')
