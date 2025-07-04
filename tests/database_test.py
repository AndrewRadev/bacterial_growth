import os
import unittest
from uuid import uuid4
from decimal import Decimal
from datetime import datetime, UTC

import db
from app.model.lib.db import execute_text
from app.model.orm import (
    Bioreplicate,
    Community,
    CommunityStrain,
    Compartment,
    Experiment,
    ExperimentCompartment,
    Measurement,
    MeasurementContext,
    MeasurementTechnique,
    Metabolite,
    ModelingRequest,
    Perturbation,
    Project,
    Strain,
    Study,
    StudyMetabolite,
    StudyUser,
    Submission,
    Taxon,
    User,
)


class DatabaseTest(unittest.TestCase):
    def setUp(self):
        # Don't truncate diff output:
        self.maxDiff = None

        self.assertEqual(
            os.environ.get('APP_ENV'),
            'test',
            "Make sure you `import tests.init` before anything else in the test",
        )

        self.db_conn = db.get_connection()
        self.db_session = db.get_session(conn=self.db_conn)

        # Clean up database state before each test:
        tables = execute_text(self.db_session, 'SHOW TABLES').scalars().all()
        for table in tables:
            if table != 'MigrationVersions':
                execute_text(self.db_session, f'DELETE FROM {table}')
        self.db_session.commit()

    def tearDown(self):
        self.db_session.close()

    def create_taxon(self, **params):
        self.ncbi_id = getattr(self, 'ncbi_id', 0) + 1
        params = {
            'ncbiId': str(self.ncbi_id),
            'name':   f"Taxon {self.ncbi_id}",
            **params,
        }

        return self._create_orm_record(Taxon, params)

    def create_metabolite(self, **params):
        self.metabolite_id = getattr(self, 'metabolite_id', 0) + 1
        params = {
            'chebiId': f"CHEBI:{self.metabolite_id}",
            'name':    f"Metabolite {self.metabolite_id}",
            **params,
        }

        return self._create_orm_record(Metabolite, params)

    def create_project(self, **params):
        project_id = Project.generate_public_id(self.db_session)
        project_uuid = str(uuid4())

        params = {
            'publicId': project_id,
            'name':     f"Project {project_id}",
            'uuid':     project_uuid,
            **params,
        }

        return self._create_orm_record(Project, params)

    def create_study(self, **params):
        study_id = Study.generate_public_id(self.db_session)
        study_uuid = str(uuid4())

        project_uuid = self._get_or_create_dependency(params, 'projectUuid', ('project', 'uuid'))

        params = {
            'publicId':    study_id,
            'projectUuid': project_uuid,
            'name':        f"Study {study_id}",
            'uuid':        study_uuid,
            'timeUnits':   's',
            **params,
        }

        return self._create_orm_record(Study, params)

    def create_study_user(self, **params):
        user_uuid = str(uuid4())
        study_uuid = self._get_or_create_dependency(params, 'studyUniqueID', ('study', 'uuid'))

        params = {
            'studyUniqueID': study_uuid,
            'userUniqueID':  user_uuid,
            **params,
        }

        return self._create_orm_record(StudyUser, params)

    def create_compartment(self, **params):
        self.compartment_sequence = getattr(self, 'compartment_sequence', 0) + 1

        study_id = self._get_or_create_dependency(params, 'studyId', ('study', 'publicId'))

        params = {
            'studyId':    study_id,
            'name':       f"Compartment {self.compartment_sequence}",
            'mediumName': 'WC anaerobe broth',
            **params,
        }

        return self._create_orm_record(Compartment, params)

    def create_experiment_compartment(self, **params):
        return self._create_orm_record(ExperimentCompartment, params)

    def create_experiment(self, **params):
        self.experiment_sequence = getattr(self, 'experiment_sequence', 0) + 1

        study_id = self._get_or_create_dependency(params, 'studyId', ('study', 'publicId'))
        public_id = Experiment.generate_public_id(self.db_session)

        params = {
            'studyId': study_id,
            'name':    f"Experiment {self.experiment_sequence}",
            'publicId': public_id,
            **params,
        }

        return self._create_orm_record(Experiment, params)

    def create_bioreplicate(self, **params):
        # Note: this is just a sequential number to ensure unique naming
        self.bioreplicate_uuid = getattr(self, 'bioreplicate_uuid', 0) + 1
        name = f"Bioreplicate {self.bioreplicate_uuid}"

        study_id        = self._get_or_create_dependency(params, 'studyId', ('study', 'publicId'))
        experiment_uuid = self._get_or_create_dependency(params, 'experimentId', ('experiment', 'id'), studyId=study_id)

        params = {
            'name':         name,
            'studyId':      study_id,
            'experimentId': experiment_uuid,
            **params,
        }

        return self._create_orm_record(Bioreplicate, params)

    def create_strain(self, **params):
        study_id = self._get_or_create_dependency(params, 'studyId', ('study', 'publicId'))
        self.ncbi_id = getattr(self, 'ncbi_id', 0) + 1

        params = {
            'name':        'Member 1',
            'description': 'Member 1',
            'studyId':     study_id,
            'defined':     True,
            'NCBId':       self.ncbi_id,
            **params,
        }

        return self._create_orm_record(Strain, params)

    def create_study_metabolite(self, **params):
        study_id = self._get_or_create_dependency(params, 'studyId', ('study', 'publicId'))
        chebi_id = self._get_or_create_dependency(params, 'chebiId', ('metabolite', 'chebiId'))

        params = {
            'studyId': study_id,
            'chebi_id': chebi_id,
            **params,
        }

        return self._create_orm_record(StudyMetabolite, params)

    def create_measurement(self, **params):
        study_id   = self._get_or_create_dependency(params, 'studyId', ('study', 'publicId'))
        context_id = self._get_or_create_dependency(params, 'contextId', ('measurement_context', 'id'))

        params = {
            'studyId':       study_id,
            'contextId':     context_id,
            'timeInSeconds': 3600,
            'value':         Decimal('100.000'),
            **params,
        }

        return self._create_orm_record(Measurement, params)

    def create_measurement_technique(self, **params):
        study_uuid = self._get_or_create_dependency(params, 'studyUniqueID', ('study', 'uuid'))

        params = {
            'type': 'fc',
            'subjectType': 'bioreplicate',
            'units': '',
            'studyUniqueID': study_uuid,
            **params,
        }

        return self._create_orm_record(MeasurementTechnique, params)

    def create_measurement_context(self, **params):
        study_id        = self._get_or_create_dependency(params, 'studyId', ('study', 'publicId'))
        bioreplicate_id = self._get_or_create_dependency(params, 'bioreplicateId', ('bioreplicate', 'id'))
        compartment_id  = self._get_or_create_dependency(params, 'compartmentId', ('compartment', 'id'))
        technique_id    = self._get_or_create_dependency(params, 'id', ('measurement_technique', 'id'))

        params = {
            'studyId':        study_id,
            'bioreplicateId': bioreplicate_id,
            'compartmentId':  compartment_id,
            'techniqueId':    technique_id,
            **params,
        }

        return self._create_orm_record(MeasurementContext, params)

    def create_submission(self, **params):
        """
        A special case of a model factory: We do not create dependencies,
        because a submission is supposed to be initialized with UUIDs that the
        Project and Study are created from.
        """
        params = {
            'studyUniqueID': str(uuid4()),
            'projectUniqueID': str(uuid4()),
            'userUniqueID': str(uuid4()),
            'studyDesign': {
                'timeUnits': 'h',
                'project': {
                    'name': 'Test project',
                },
                'study': {
                    'name': 'Test study',
                },
                **params.get('studyDesign', {})
            },
            **params,
        }

        return self._create_orm_record(Submission, params)

    def create_modeling_request(self, **params):
        study_id = self._get_or_create_dependency(params, 'studyId', ('study', 'publicId'))

        params = {
            'type':    'baranyi_roberts',
            'studyId': study_id,
            **params,
        }

        return self._create_orm_record(ModelingRequest, params)

    def create_community(self, **params):
        study_id = self._get_or_create_dependency(params, 'studyId', ('study', 'publicId'))

        params = {
            'name':    'C1',
            'studyId': study_id,
            **params,
        }

        return self._create_orm_record(Community, params)

    def create_community_strain(self, **params):
        community_id = self._get_or_create_dependency(params, 'communityId', ('community', 'id'))
        strain_id    = self._get_or_create_dependency(params, 'strainId', ('strain', 'id'))

        params = {
            'communityId': community_id,
            'strainId': strain_id,
            **params,
        }

        return self._create_orm_record(CommunityStrain, params)

    def create_perturbation(self, **params):
        experiment_id = self._get_or_create_dependency(params, 'experimentId', ('experiment', 'id'))
        study_id      = self._get_or_create_dependency(params, 'studyId', ('study', 'publicId'))

        params = {
            'experimentId': experiment_id,
            'studyId': study_id,
            'startTimeInSeconds': 0,
            **params,
        }

        return self._create_orm_record(Perturbation, params)

    def create_user(self, **params):
        params = {
            'name':        'Test user',
            'uuid':        str(uuid4()),
            'orcidId':     str(uuid4()),
            'orcidToken':  str(uuid4()),
            'lastLoginAt': datetime.now(UTC),
            **params,
        }

        return self._create_orm_record(User, params)

    def _create_orm_record(self, model_class, params):
        instance = model_class(**params)
        self.db_session.add(instance)
        self.db_session.flush()

        return instance

    def _get_or_create_dependency(self, params, key_name, object_name, **dependency_params):
        """
        Example call:

            self._get_or_create_dependency(params, 'studyId', ('study', 'publicId'))

        If the 'studyId' key is given in `params`, it is returned, otherwise,
        the `create_study` factory is called and the `publicId` property is
        taken from the output and returned.
        """
        if isinstance(object_name, tuple):
            (object_name, object_key_name) = object_name
        else:
            object_key_name = key_name

        if key_name in params:
            key_value = params[key_name]
        else:
            creator_func = getattr(self, f"create_{object_name}")
            dependency_params = {
                **dependency_params,
                **params.pop(object_name, {})
            }

            object = creator_func(**dependency_params)
            key_value = getattr(object, object_key_name)

        return key_value
