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
    CustomModel,
    Experiment,
    ExperimentCompartment,
    Measurement,
    MeasurementContext,
    MeasurementTechnique,
    Metabolite,
    ModelingResult,
    PageVisit,
    Perturbation,
    Project,
    Study,
    StudyMetabolite,
    StudyStrain,
    StudyTechnique,
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
        study_id = self._get_or_create_dependency(params, 'studyId', ('study', 'publicId'))
        public_id = Experiment.generate_public_id(self.db_session)

        params = {
            'studyId': study_id,
            'name':    f"Experiment {public_id}",
            'publicId': public_id,
            **params,
        }

        return self._create_orm_record(Experiment, params)

    def create_bioreplicate(self, **params):
        # Note: this is just a sequential number to ensure unique naming
        self.bioreplicate_id = getattr(self, 'bioreplicate_id', 0) + 1
        name = f"Bioreplicate {self.bioreplicate_id}"

        experiment_id = self._get_or_create_dependency(params, 'experimentId', ('experiment', 'publicId'))

        params = {
            'name':         name,
            'experimentId': experiment_id,
            **params,
        }

        return self._create_orm_record(Bioreplicate, params)

    def create_study_strain(self, **params):
        study_id = self._get_or_create_dependency(params, 'studyId', ('study', 'publicId'))
        ncbi_id  = self._get_or_create_dependency(params, 'ncbiId', ('taxon', 'ncbiId'))

        params = {
            'name':        'Member 1',
            'description': 'Member 1',
            'studyId':     study_id,
            'defined':     True,
            'ncbiId':      ncbi_id,
            **params,
        }

        return self._create_orm_record(StudyStrain, params)

    def create_study_metabolite(self, **params):
        study_id = self._get_or_create_dependency(params, 'studyId', ('study', 'publicId'))
        chebi_id = self._get_or_create_dependency(params, 'chebiId', ('metabolite', 'chebiId'))

        params = {
            'studyId': study_id,
            'chebiId': chebi_id,
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

    def create_study_technique(self, **params):
        study_id = self._get_or_create_dependency(params, 'studyId', ('study', 'publicId'))

        params = {
            'type': 'fc',
            'subjectType': 'bioreplicate',
            'studyId': study_id,
            'units': '',
            **params,
        }

        return self._create_orm_record(StudyTechnique, params)

    def create_measurement_technique(self, **params):
        study_id           = self._get_or_create_dependency(params, 'studyId', ('study', 'publicId'))
        study_technique_id = self._get_or_create_dependency(params, 'studyTechniqueId', ('study_technique', 'id'))

        params = {
            'type': 'fc',
            'subjectType': 'bioreplicate',
            'units': '',
            'studyId': study_id,
            'studyTechniqueId': study_technique_id,
            **params,
        }

        return self._create_orm_record(MeasurementTechnique, params)

    def create_measurement_context(self, **params):
        study_id        = self._get_or_create_dependency(params, 'studyId', ('study', 'publicId'))
        bioreplicate_id = self._get_or_create_dependency(params, 'bioreplicateId', ('bioreplicate', 'id'))
        compartment_id  = self._get_or_create_dependency(params, 'compartmentId', ('compartment', 'id'))
        technique_id    = self._get_or_create_dependency(params, 'id', ('measurement_technique', 'id'))

        subject_id = self._get_or_create_dependency(params, 'subjectId', ('bioreplicate', 'id'))

        params = {
            'studyId':        study_id,
            'bioreplicateId': bioreplicate_id,
            'compartmentId':  compartment_id,
            'techniqueId':    technique_id,
            'subjectType':    'bioreplicate',
            'subjectId':      subject_id,
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

    def create_modeling_result(self, **params):
        measurement_context_id = self._get_or_create_dependency(params, 'measurementContextId', ('measurement_context', 'id'))

        if 'type' in params and params['type'].startswith('custom_'):
            custom_model_id = self._get_or_create_dependency(params, 'customModelId', ('custom_model', 'id'))
        else:
            custom_model_id = None

        params = {
            'type':                 'baranyi_roberts',
            'measurementContextId': measurement_context_id,
            'customModelId':        custom_model_id,
            **params,
        }

        return self._create_orm_record(ModelingResult, params)

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
        strain_id    = self._get_or_create_dependency(params, 'strainId', ('study_strain', 'id'))

        params = {
            'communityId': community_id,
            'strainId': strain_id,
            **params,
        }

        return self._create_orm_record(CommunityStrain, params)

    def create_perturbation(self, **params):
        experiment_id = self._get_or_create_dependency(params, 'experimentId', ('experiment', 'publicId'))

        params = {
            'experimentId': experiment_id,
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

    def create_custom_model(self, **params):
        study_id = self._get_or_create_dependency(params, 'studyId', ('study', 'publicId'))

        params = {
            'name': 'Custom Model',
            'studyId': study_id,
            **params,
        }

        return self._create_orm_record(CustomModel, params)

    def create_page_visit(self, **params):
        params = {
            'path': '/',
            'ip': '127.0.0.1',
            'userAgent': 'Mozilla/5.0 (X11; Linux x86_64; rv:147.0) Gecko/20100101 Firefox/147.0',
            'uuid': str(uuid4()),
            **params,
        }

        return self._create_orm_record(PageVisit, params)

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
            key_value = params.pop(key_name)
        else:
            creator_func = getattr(self, f"create_{object_name}")
            dependency_params = {
                **dependency_params,
                **params.pop(object_name, {})
            }

            object = creator_func(**dependency_params)
            key_value = getattr(object, object_key_name)

        return key_value
