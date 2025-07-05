import tests.init  # noqa: F401

import unittest

from app.model.orm import Compartment
from tests.database_test import DatabaseTest


class TestCompartment(DatabaseTest):
    def test_successful_creation(self):
        study = self.create_study()

        compartment = Compartment(
            studyId=study.publicId,
            name="Test compartment",
            mediumName='Wilkins-Chalgren Anaerobe Broth (WC)',
        )
        self.db_session.add(compartment)
        self.db_session.flush()

        self.assertIsNotNone(compartment.id)

    def test_describe_differences(self):
        c1 = self.create_compartment(name="C1", initialPh=7, initialTemperature=37)
        c2 = self.create_compartment(name="C2", initialPh=3, initialTemperature=37)
        c3 = self.create_compartment(name="C3", initialPh=8, initialTemperature=40)

        diff = c1.diff(c2)
        self.assertEqual(set(diff), {('initial pH', 7, 3)})

        diff = c2.diff(c1)
        self.assertEqual(set(diff), {('initial pH', 3, 7)})

        diff = c1.diff(c3)
        self.assertEqual(set(diff), {
            ('initial pH', 7, 8),
            ('initial temperature', 37, 40),
        })


if __name__ == '__main__':
    unittest.main()
