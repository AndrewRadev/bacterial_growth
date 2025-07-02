import tests.init  # noqa: F401

import unittest

from app.model.orm import ModelingResult
from tests.database_test import DatabaseTest


class TestPerturbation(DatabaseTest):
    def test_textual_description(self):
        pass


if __name__ == '__main__':
    unittest.main()
