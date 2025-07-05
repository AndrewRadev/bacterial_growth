import tests.init  # noqa: F401

import unittest
from datetime import datetime, timedelta, UTC

from freezegun import freeze_time
import sqlalchemy as sql
from sqlalchemy.orm.attributes import flag_modified

from app.model.orm import (
    Community,
    Compartment,
    Experiment,
    Project,
    Strain,
    Study,
)
from app.view.forms.submission_form import SubmissionForm
from app.model.lib.submission_process import (
    _clear_study,
    _save_project,
    _save_study,
    _save_compartments,
    _save_communities,
    _save_experiments,
    _save_measurement_techniques,
    _create_average_measurements,
)
from tests.database_test import DatabaseTest


class TestSubmissionProcess(DatabaseTest):
    def setUp(self):
        super().setUp()

        self.submission = self.create_submission(
            studyDesign={
                'project': {'name': 'Test project'},
                'study':   {'name': 'Test study'}
            }
        )

    def test_project_and_study_creation(self):
        submission_form = SubmissionForm(submission_id=self.submission.id, db_session=self.db_session)

        # Creating a new project and study:
        project = self.db_session.get(Project, self.submission.projectUniqueID)
        study   = self.db_session.get(Study,   self.submission.studyUniqueID)
        self.assertIsNone(project)
        self.assertIsNone(study)

        _save_project(self.db_session, submission_form)
        _save_study(self.db_session, submission_form)
        self.db_session.commit()

        project = self.db_session.get(Project, self.submission.projectUniqueID)
        study   = self.db_session.get(Study,   self.submission.studyUniqueID)
        self.assertIsNotNone(project)
        self.assertIsNotNone(study)
        self.assertEqual(project.name, 'Test project')
        self.assertEqual(study.name, 'Test study')

        # Updating the existing project and study:
        submission_form.update_project({
            'project_uuid': self.submission.projectUniqueID,
            'study_uuid':   self.submission.studyUniqueID,
            'study_name':   'Updated study name',
            'project_name': 'Updated project name',
        })

        # Save the study, the project is not updated yet:
        _save_study(self.db_session, submission_form)
        self.db_session.flush()

        self.assertEqual(project.name, 'Test project')
        self.assertEqual(study.name, 'Updated study name')

        # Save project, both names are updated:
        _save_project(self.db_session, submission_form)
        self.db_session.flush()

        self.assertEqual(project.name, 'Updated project name')
        self.assertEqual(study.name, 'Updated study name')

    def test_study_publication_state(self):
        submission_form = SubmissionForm(submission_id=self.submission.id, db_session=self.db_session)

        with freeze_time(datetime.now(UTC)) as frozen_time:
            _save_project(self.db_session, submission_form)
            _save_study(self.db_session, submission_form)
            self.db_session.flush()

            study = self.db_session.get(Study, self.submission.studyUniqueID)

            # Initial study state: not published, can't be published
            self.assertFalse(study.isPublishable)
            self.assertFalse(study.isPublished)
            self.assertFalse(study.publish())

            # After 24 hours, it can be published:
            frozen_time.tick(delta=timedelta(hours=24, seconds=1))

            self.assertTrue(study.isPublishable)
            self.assertFalse(study.isPublished)

            # After explicitly publishing, it's published
            self.assertTrue(study.publish())
            self.db_session.add(study)
            self.db_session.commit()

            self.assertTrue(study.isPublishable)
            self.assertTrue(study.isPublished)

    def test_compartment_creation(self):
        submission_form = SubmissionForm(submission_id=self.submission.id, db_session=self.db_session)
        submission_form.update_study_design({
            'compartments': [{
                'name': 'WC',
                'mediumName': 'Wilkins-Chalgren',
            }, {
                'name': 'Mucin',
                'mediumName': 'Mucin',
            }]
        })
        submission_form.save()

        # Creating compartments defined by the self.submission
        study        = _save_study(self.db_session, submission_form)
        compartments = _save_compartments(self.db_session, submission_form, study)

        self.db_session.flush()

        self.assertEqual(['WC', 'Mucin'], [c.name for c in compartments])
        self.assertEqual(compartments, study.compartments)
        self.assertEqual(2, self.db_session.scalar(sql.func.count(Compartment.id)))

        # Remove all compartments
        self.submission.studyDesign['compartments'] = []
        compartments = _save_compartments(self.db_session, submission_form, study)

        self.db_session.flush()
        self.db_session.refresh(study)

        self.assertEqual([], [c.name for c in compartments])
        self.assertEqual(compartments, study.compartments)
        self.assertEqual(0, self.db_session.scalar(sql.func.count(Compartment.id)))

    def test_community_creation(self):
        t_ri = self.create_taxon(name='Roseburia intestinalis')
        t_bh = self.create_taxon(name='Blautia hydrogenotrophica')

        submission_form = SubmissionForm(submission_id=self.submission.id, db_session=self.db_session)
        submission_form.update_study_design({
            'project': {'name': 'Test project'},
            'study':   {'name': 'Test study'},

            'custom_strains': [{
                'name': 'Custom strain',
                'description': 'test',
                'species': t_ri.ncbiId,
            }],

            'communities': [{
                'name': 'Full',
                'strainIdentifiers': [
                    f"existing|{t_ri.ncbiId}",
                    f"existing|{t_bh.ncbiId}",
                    'custom|Custom strain',
                ],
            }, {
                'name': 'RI',
                'strainIdentifiers': [f"existing|{t_ri.ncbiId}"]
            }, {
                'name': 'Blank',
                'strainIdentifiers': [],
            }]
        })

        # Creating compartments defined by the submission
        study       = _save_study(self.db_session, submission_form)
        communities = _save_communities(self.db_session, submission_form, study, user_uuid='user1')

        self.db_session.flush()

        self.assertEqual(['Full', 'RI', 'Blank'], [c.name for c in communities])
        self.assertEqual(communities, study.communities)
        self.assertEqual(3, self.db_session.scalar(sql.func.count(Community.id)))

        # Check existence of strains:
        s_ri     = self.db_session.scalar(sql.select(Strain).where(Strain.NCBId == t_ri.ncbiId))
        s_bh     = self.db_session.scalar(sql.select(Strain).where(Strain.NCBId == t_bh.ncbiId))
        s_custom = self.db_session.scalar(sql.select(Strain).where(Strain.name == 'Custom strain'))

        c_full, c_ri, c_blank = communities
        self.assertEqual(set(c_full.strains), {s_ri, s_bh, s_custom})

        # Remove all communities
        self.submission.studyDesign['communities'] = []
        communities = _save_communities(self.db_session, submission_form, study, user_uuid='user1')

        self.db_session.flush()
        self.db_session.refresh(study)

        self.assertEqual([], [c.name for c in communities])
        self.assertEqual(communities, study.communities)
        self.assertEqual(0, self.db_session.scalar(sql.func.count(Community.id)))

    def test_experiment_creation(self):
        t_ri = self.create_taxon(name='Roseburia intestinalis')

        submission_form = SubmissionForm(submission_id=self.submission.id, db_session=self.db_session)
        submission_form.update_study_design({
            'timeUnits': 'h',
            'compartments': [
                {'name': 'WC',    'mediumName': 'WC'},
                {'name': 'MUCIN', 'mediumName': 'WC'}
            ],
            'communities': [
                {'name': 'RI', 'strainIdentifiers': [f"existing|{t_ri.ncbiId}"]},
            ],

            'experiments': [{
                'name': 'RI',
                'description': 'RI experiment',
                'cultivationMode': 'batch',
                'communityName': 'RI',
                'compartmentNames': ['WC', 'MUCIN'],
                'bioreplicates': [
                    {'name': 'RI_1'},
                    {'name': 'RI_2'},
                    {'name': 'RI_3'},
                ],
                'perturbations': [{
                    'description': 'Change everything',
                    'startTime': 10,
                    'endTime': 20,
                    'removedCompartmentName': 'MUCIN',
                    'addedCompartmentName': '',
                    'newCommunityName': 'RI',
                    'oldCommunityName': '',
                }]
            }]
        })

        # Create dependencies
        study        = _save_study(self.db_session, submission_form)
        communities  = _save_communities(self.db_session, submission_form, study, user_uuid='user1')
        compartments = _save_compartments(self.db_session, submission_form, study)

        experiments = _save_experiments(self.db_session, submission_form, study)
        flag_modified(submission_form.submission, 'studyDesign')
        submission_form.save()

        self.db_session.commit()

        self.assertEqual(len(experiments), 1)
        self.assertEqual(experiments, study.experiments)

        experiment = experiments[0]

        self.assertEqual(experiment.community, communities[0])
        self.assertEqual(len(experiment.compartments), 2)
        self.assertEqual(experiment.compartments, compartments)

        self.assertEqual(len(experiment.perturbations), 1)
        self.assertEqual(experiment.perturbations[0].newCommunityId, communities[0].id)

        self.assertEqual(len(experiment.bioreplicates), 3)
        self.assertEqual({'RI_1', 'RI_2', 'RI_3'}, {b.name for b in experiment.bioreplicates})

        # Generated experiment public ID is saved in the form:
        self.assertRegex(submission_form.submission.studyDesign['experiments'][0]['publicId'], r'^EMGDB\d+$')

        # Check that recreating experiments from the same study maintains their public ids:
        experiment_public_id = experiment.publicId

        # Create a new experiment
        new_experiment = self.create_experiment()
        self.assertNotEqual(experiment_public_id, new_experiment.publicId)

        self.db_session.refresh(study)

        # Redo upload and check that the public ids are the same:
        _clear_study(study)

        # Experiment is not deleted:
        self.assertIsNotNone(self.db_session.get(Experiment, experiment.id))

        communities  = _save_communities(self.db_session, submission_form, study, user_uuid='user1')
        compartments = _save_compartments(self.db_session, submission_form, study)

        experiments = _save_experiments(self.db_session, submission_form, study)

        self.assertEqual(submission_form.submission.studyDesign['experiments'][0]['publicId'], experiment_public_id)

    def test_experiment_removal(self):
        t_ri = self.create_taxon(name='Roseburia intestinalis')

        submission_form = SubmissionForm(submission_id=self.submission.id, db_session=self.db_session)
        submission_form.update_study_design({
            'timeUnits': 'h',
            'compartments': [{'name': 'WC', 'mediumName': 'WC'}],
            'communities': [{'name': 'RI', 'strainIdentifiers': [f"existing|{t_ri.ncbiId}"]}],

            'experiments': [{
                'name': 'RI_1',
                'description': 'RI experiment',
                'cultivationMode': 'batch',
                'communityName': 'RI',
                'compartmentNames': ['WC'],
                'bioreplicates': [{'name': 'RI_1_1'}],
                'perturbations': [],
            }, {
                'name': 'RI_2',
                'description': 'RI experiment',
                'cultivationMode': 'batch',
                'communityName': 'RI',
                'compartmentNames': ['WC'],
                'bioreplicates': [{'name': 'RI_2_1'}],
                'perturbations': [],
            }]
        })

        # Create dependencies
        study        = _save_study(self.db_session, submission_form)
        communities  = _save_communities(self.db_session, submission_form, study, user_uuid='user1')
        compartments = _save_compartments(self.db_session, submission_form, study)

        experiments = _save_experiments(self.db_session, submission_form, study)
        flag_modified(submission_form.submission, 'studyDesign')
        submission_form.save()
        self.db_session.commit()

        experiment_public_ids = [e.publicId for e in experiments]
        experiment_ids        = [e.id for e in experiments]

        # Both experiments exist in the database:
        self.assertIsNotNone(self.db_session.get(Experiment, experiment_ids[0]))
        self.assertIsNotNone(self.db_session.get(Experiment, experiment_ids[1]))

        # Remove experiment 2 from list, add a new one:
        experiment_data = submission_form.submission.studyDesign['experiments']
        experiment_data.pop()
        experiment_data.append({
            'name': 'RI_3',
            'description': 'RI experiment',
            'cultivationMode': 'batch',
            'communityName': 'RI',
            'compartmentNames': ['WC'],
            'bioreplicates': [{'name': 'RI_2_1'}],
            'perturbations': [],
        })

        # Redo upload
        _clear_study(study)

        communities  = _save_communities(self.db_session, submission_form, study, user_uuid='user1')
        compartments = _save_compartments(self.db_session, submission_form, study)

        experiments = _save_experiments(self.db_session, submission_form, study)
        flag_modified(submission_form.submission, 'studyDesign')
        submission_form.save()
        self.db_session.commit()

        self.assertEqual([e.name for e in experiments], ["RI_1", "RI_3"])

        # First experiment id doesn't change, the second one does:
        new_experiment_public_ids = [e.publicId for e in experiments]

        self.assertEqual(experiment_public_ids[0], new_experiment_public_ids[0])
        self.assertNotEqual(experiment_public_ids[1], new_experiment_public_ids[1])

        # The first experiment exists in the database, the second one doesn't
        self.assertIsNotNone(self.db_session.get(Experiment, experiment_ids[0]))
        self.assertIsNone(self.db_session.get(Experiment, experiment_ids[1]))

    def test_measurement_technique_creation(self):
        m1 = self.create_metabolite(name='pyruvate')
        m2 = self.create_metabolite(name='butyrate')

        submission_form = SubmissionForm(submission_id=self.submission.id, db_session=self.db_session)
        submission_form.update_study_design({
            'techniques': [{
                'type': 'od',
                'units': '',
                'includeStd': False,
                'subjectType': 'bioreplicate',
                'metaboliteIds': [],
            }, {
                'type': 'fc',
                'units': 'Cells/mL',
                'includeStd': True,
                'subjectType': 'strain',
                'metaboliteIds': [],
            }, {
                'type': 'metabolite',
                'units': 'mM',
                'includeStd': False,
                'subjectType': 'strain',
                'metaboliteIds': [m1.chebiId, m2.chebiId],
            }]
        })
        submission_form.save()

        study = _save_study(self.db_session, submission_form)

        techniques = _save_measurement_techniques(self.db_session, submission_form, study)
        self.db_session.flush()

        self.assertEqual(len(techniques), 3)
        self.assertEqual(techniques, study.measurementTechniques)
        self.assertEqual({m.name for m in study.metabolites}, {'pyruvate', 'butyrate'})

    def test_average_measurement_creation(self):
        experiment = self.create_experiment(name="e1")
        study = experiment.study

        c1 = self.create_compartment()
        self.create_experiment_compartment(compartmentId=c1.id, experimentId=experiment.id)

        mt = self.create_measurement_technique(subjectType='bioreplicate', studyId=study.publicId)

        b1 = self.create_bioreplicate(name="b1", experimentId=experiment.id)
        mc1 = self.create_measurement_context(
            subjectId=b1.id,
            subjectType='bioreplicate',
            bioreplicateId=b1.id,
            techniqueId=mt.id,
            compartmentId=c1.id,
        )
        for i, value in enumerate([10, 20, 30]):
            self.create_measurement(timeInSeconds=i, value=value, contextId=mc1.id)

        b2 = self.create_bioreplicate(name="b2", experimentId=experiment.id)
        mc2 = self.create_measurement_context(
            subjectId=b2.id,
            subjectType='bioreplicate',
            bioreplicateId=b2.id,
            techniqueId=mt.id,
            compartmentId=c1.id,
        )
        for i, value in enumerate([20, 40, 60]):
            self.create_measurement(timeInSeconds=i, value=value, contextId=mc2.id)

        self.assertEqual({b.name for b in experiment.bioreplicates}, {"b1", "b2"})
        _create_average_measurements(self.db_session, study, experiment)
        self.db_session.refresh(experiment)
        self.assertEqual({b.name for b in experiment.bioreplicates}, {"b1", "b2", "Average(e1)"})

        average_bioreplicate = next(b for b in experiment.bioreplicates if b.name == "Average(e1)")
        self.assertEqual(average_bioreplicate.calculationType, 'average')
        self.assertEqual([int(m.value) for m in average_bioreplicate.measurements], [15, 30, 45])

        # Don't create averages if their time points don't match
        b3 = self.create_bioreplicate(name="b3", experimentId=experiment.id)
        mc3 = self.create_measurement_context(
            subjectId=b3.id,
            subjectType='bioreplicate',
            bioreplicateId=b3.id,
            techniqueId=mt.id,
            compartmentId=c1.id,
            studyId=study.publicId,
        )
        for i, value in enumerate([30, 50, 70]):
            # Time points offset by 1:
            self.create_measurement(timeInSeconds=i + 1, value=value, contextId=mc3.id)

        self.db_session.delete(average_bioreplicate)
        self.db_session.flush()

        self.db_session.refresh(experiment)

        # Average bioreplicate doesn't get created:
        self.assertEqual({b.name for b in experiment.bioreplicates}, {"b1", "b2", "b3"})
        _create_average_measurements(self.db_session, study, experiment)
        self.db_session.refresh(experiment)
        self.assertEqual({b.name for b in experiment.bioreplicates}, {"b1", "b2", "b3"})


if __name__ == '__main__':
    unittest.main()
