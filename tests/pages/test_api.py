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

    def test_measurement_json(self):
        study        = self.create_study(publishedAt=datetime.now(UTC))
        experiment   = self.create_experiment(studyId=study.publicId)
        bioreplicate = self.create_bioreplicate(name='B1', experimentId=experiment.publicId)

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

        # Unrelated measurement, not included in the count
        self.create_measurement()

        self.db_session.commit()

        response = self.client.get(f"/api/v1/measurement-context/{measurement_context.id}.json")
        self.assertEqual(response.status, '200 OK')

        response_json = self._get_json(response)

        self.assertEqual(response_json['id'], measurement_context.id)
        self.assertEqual(response_json['studyId'], study.publicId)
        self.assertEqual(response_json['experimentId'], experiment.publicId)
        self.assertEqual(response_json['techniqueType'], 'fc')
        self.assertEqual(response_json['techniqueUnits'], '')
        self.assertEqual(response_json['bioreplicateName'], 'B1')
        self.assertEqual(response_json['measurementCount'], 3)

    def test_non_published_measurement_endpoints(self):
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

        response1 = self.client.get(f"/api/v1/measurement-context/{measurement_context.id}.json")
        self.assertEqual(response1.status, '404 NOT FOUND')

        response2 = self.client.get(f"/api/v1/measurement-context/{measurement_context.id}.csv")
        self.assertEqual(response2.status, '404 NOT FOUND')
        self.assertEqual(response2.data, b'404 Not found')

    def test_bioreplicate_csv(self):
        study        = self.create_study(publishedAt=datetime.now(UTC))
        experiment   = self.create_experiment(studyId=study.publicId)
        bioreplicate = self.create_bioreplicate(experimentId=experiment.publicId)
        strain       = self.create_strain(studyId=study.publicId)

        for subject, subject_type in ((bioreplicate, 'bioreplicate'), (strain, 'strain')):
            measurement_context = self.create_measurement_context(
                studyId=study.publicId,
                bioreplicateId=bioreplicate.id,
                subjectId=subject.id,
                subjectType=subject_type,
            )
            for i in range(1, 4):
                self.create_measurement(
                    contextId=measurement_context.id,
                    timeInSeconds=(i * 3600),
                    value=(i * 10),
                )

        self.db_session.commit()

        response = self.client.get(f"/api/v1/bioreplicate/{bioreplicate.id}.csv")
        self.assertEqual(response.status, '200 OK')

        response_df = self._get_csv(response)

        self.assertEqual(response_df.columns.tolist(), ['measurementContextId', 'time', 'value', 'std'])
        self.assertEqual(response_df['time'].tolist(), [1, 2, 3, 1, 2, 3])
        self.assertEqual(response_df['value'].tolist(), [10, 20, 30, 10, 20, 30])
        self.assertTrue(response_df['std'].isna().all())

    def test_bioreplicate_json(self):
        study        = self.create_study(publishedAt=datetime.now(UTC))
        experiment   = self.create_experiment(studyId=study.publicId)
        bioreplicate = self.create_bioreplicate(name='B1', experimentId=experiment.publicId)

        measurement_context = self.create_measurement_context(
            studyId=study.publicId,
            bioreplicateId=bioreplicate.id,
            subjectId=bioreplicate.id,
            subjectType='bioreplicate',
        )

        self.db_session.commit()

        response = self.client.get(f"/api/v1/bioreplicate/{bioreplicate.id}.json")
        self.assertEqual(response.status, '200 OK')

        response_json = self._get_json(response)

        self.assertEqual(response_json['id'], bioreplicate.id)
        self.assertEqual(response_json['studyId'], study.publicId)
        self.assertEqual(response_json['experimentId'], experiment.publicId)
        self.assertEqual(response_json['name'], 'B1')
        self.assertEqual(len(response_json['measurementContexts']), 1)
        self.assertEqual(response_json['measurementContexts'][0]['id'], measurement_context.id)

    def test_search(self):
        s1 = self.create_study(publishedAt=datetime.now(UTC))
        s2 = self.create_study(publishedAt=datetime.now(UTC))

        b1 = self.create_bioreplicate(experimentId=self.create_experiment(studyId=s1.publicId).publicId)
        b2 = self.create_bioreplicate(experimentId=self.create_experiment(studyId=s1.publicId).publicId)
        b3 = self.create_bioreplicate(experimentId=self.create_experiment(studyId=s2.publicId).publicId)
        b4 = self.create_bioreplicate(experimentId=self.create_experiment(studyId=s2.publicId).publicId)

        roseburia = self.create_strain(name='Roseburia')
        blautia   = self.create_strain(name='Blautia')

        glucose   = self.create_metabolite(name="glucose")
        trehalose = self.create_metabolite(name="trehalose")

        mc1 = self.create_measurement_context(
            studyId=s1.publicId,
            bioreplicateId=b1.id,
            subjectId=roseburia.id,
            subjectType='strain',
        )
        mc2 = self.create_measurement_context(
            studyId=s1.publicId,
            bioreplicateId=b2.id,
            subjectId=blautia.id,
            subjectType='strain',
        )
        mc3 = self.create_measurement_context(
            studyId=s2.publicId,
            bioreplicateId=b3.id,
            subjectId=roseburia.id,
            subjectType='strain',
        )
        mc4 = self.create_measurement_context(
            studyId=s2.publicId,
            bioreplicateId=b4.id,
            subjectId=glucose.id,
            subjectType='metabolite',
        )
        mc5 = self.create_measurement_context(
            studyId=s2.publicId,
            bioreplicateId=b4.id,
            subjectId=trehalose.id,
            subjectType='metabolite',
        )

        self.db_session.commit()

        # Searching by strain:
        response = self.client.get(f"/api/v1/search.json?strainNcbiIds={roseburia.NCBId}")
        self.assertEqual(response.status, '200 OK')
        response_json = self._get_json(response)

        self.assertEqual(sorted(response_json['studies']), sorted([s1.publicId, s2.publicId]))
        self.assertEqual(sorted(response_json['experiments']), sorted([b1.experimentId, b3.experimentId]))
        mc_ids = sorted([mc['id'] for mc in response_json['measurementContexts']])
        self.assertEqual(mc_ids, sorted([mc1.id, mc3.id]))

        response = self.client.get(f"/api/v1/search.json?strainNcbiIds={blautia.NCBId}")
        self.assertEqual(response.status, '200 OK')
        response_json = self._get_json(response)

        self.assertEqual(response_json['studies'], [s1.publicId])
        self.assertEqual(sorted(response_json['experiments']), sorted([b2.experimentId]))
        mc_ids = sorted([mc['id'] for mc in response_json['measurementContexts']])
        self.assertEqual(mc_ids, sorted([mc2.id]))

        # Searching by metabolite:
        query = trehalose.chebiId.removeprefix("CHEBI:")
        response = self.client.get(f"/api/v1/search.json?metaboliteChebiIds={query}")
        self.assertEqual(response.status, '200 OK')
        response_json = self._get_json(response)

        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response_json['studies'], [s2.publicId])
        self.assertEqual(sorted(response_json['experiments']), sorted([b4.experimentId]))
        mc_ids = sorted([mc['id'] for mc in response_json['measurementContexts']])
        self.assertEqual(mc_ids, sorted([mc5.id]))

        # Searching by both strain and metabolite returns both matches (strain OR metabolite):
        strain_query = blautia.NCBId
        metabolite_query = trehalose.chebiId.removeprefix("CHEBI:")

        response = self.client.get(f"/api/v1/search.json?strainNcbiIds={strain_query}&metaboliteChebiIds={metabolite_query}")
        self.assertEqual(response.status, '200 OK')
        response_json = self._get_json(response)

        self.assertEqual(response.status, '200 OK')
        self.assertEqual(sorted(response_json['studies']), sorted([s1.publicId, s2.publicId]))
        self.assertEqual(sorted(response_json['experiments']), sorted([b2.experimentId, b4.experimentId]))
        mc_ids = sorted([mc['id'] for mc in response_json['measurementContexts']])
        self.assertEqual(mc_ids, sorted([mc2.id, mc5.id]))

        # Searching by multiple strains and metabolites returns all matches:
        strain_query = f"{blautia.NCBId},{roseburia.NCBId}"
        metabolite_query = ','.join([
            glucose.chebiId.removeprefix("CHEBI:"),
            trehalose.chebiId.removeprefix("CHEBI:"),
        ])

        response = self.client.get(f"/api/v1/search.json?strainNcbiIds={strain_query}&metaboliteChebiIds={metabolite_query}")
        self.assertEqual(response.status, '200 OK')
        response_json = self._get_json(response)

        self.assertEqual(response.status, '200 OK')
        self.assertEqual(sorted(response_json['studies']), sorted([s1.publicId, s2.publicId]))
        self.assertEqual(
            sorted(response_json['experiments']),
            sorted([
                b1.experimentId,
                b2.experimentId,
                b3.experimentId,
                b4.experimentId,
            ]),
        )
        mc_ids = sorted([mc['id'] for mc in response_json['measurementContexts']])
        self.assertEqual(mc_ids, sorted([mc1.id, mc2.id, mc3.id, mc4.id, mc5.id]))

        # No results:
        response = self.client.get(f"/api/v1/search.json?strainNcbiIds=nonexistent")
        self.assertEqual(response.status, '200 OK')
        response_json = self._get_json(response)

        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response_json['studies'], [])
        self.assertEqual(response_json['experiments'], [])
        self.assertEqual(response_json['measurementContexts'], [])

        # No search parameters:
        response = self.client.get(f"/api/v1/search.json")
        self.assertEqual(response.status, '400 BAD REQUEST')
        self.assertTrue('error' in self._get_json(response))

        # Unknown search parameter:
        response = self.client.get(f"/api/v1/search.json?unknownSearchTerm=mistake")
        self.assertEqual(response.status, '400 BAD REQUEST')
        self.assertTrue('error' in self._get_json(response))
