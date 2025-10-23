import tests.init  # noqa: F401

import unittest

import pandas as pd

from app.model.lib.conversion import (
    convert_time,
    convert_df_units,
    convert_measurement_units,
)


class TestConversion(unittest.TestCase):
    def test_converting_df_units(self):
        df = pd.DataFrame.from_dict({
            'time':  [1, 2, 3],
            'value': [10, 20, 30],
            'std':   [2, 4, 6],
        })

        cell_df = df.copy()
        result_units = convert_df_units(cell_df, 'Cells/μL', 'Cells/mL')

        self.assertEqual(cell_df['value'].tolist(), [10_000, 20_000, 30_000])
        self.assertEqual(cell_df['std'].tolist(), [2000, 4000, 6000])
        self.assertEqual(result_units, 'Cells/mL')

        # Incompatible units: no change in values, result units are the same as
        # source units:
        result_units = convert_df_units(df, 'Cells/mL', 'mM')

        self.assertEqual(cell_df['value'].tolist(), [10_000, 20_000, 30_000])
        self.assertEqual(cell_df['std'].tolist(), [2000, 4000, 6000])
        self.assertEqual(result_units, 'Cells/mL')

        # Metabolites:
        metabolite_df = df.copy()
        result_units = convert_df_units(metabolite_df, 'mM', 'mg/L', 13)

        self.assertEqual(metabolite_df['value'].tolist(), [130, 260, 390])
        self.assertEqual(metabolite_df['std'].tolist(), [26, 52, 78])
        self.assertEqual(result_units, 'mg/L')

        # Metabolites without a mass given, no change
        result_units = convert_df_units(metabolite_df, 'mg/L', 'mM')
        self.assertEqual(metabolite_df['value'].tolist(), [130, 260, 390])
        self.assertEqual(metabolite_df['std'].tolist(), [26, 52, 78])
        self.assertEqual(result_units, 'mg/L')

    def test_cell_concentration_conversion(self):
        value = convert_measurement_units(2, 'Cells/μL', 'Cells/mL')
        self.assertEqual(value, 2000)

        value = convert_measurement_units(4000, 'Cells/mL', 'Cells/μL')
        self.assertEqual(value, 4)

        value = convert_measurement_units(2000, 'Cells/mL', 'Cells/mL')
        self.assertEqual(value, 2000)

        value = convert_measurement_units(2000, 'Cells/μL', 'pH')
        self.assertIsNone(value)

    def test_simple_metabolite_conversion(self):
        value = convert_measurement_units(2000, 'μM', 'mM')
        self.assertEqual(value, 2)

        value = convert_measurement_units(4, 'nM', 'pM')
        self.assertEqual(value, 4000)

        value = convert_measurement_units(4, 'mM', 'pM')
        self.assertEqual(value, 4_000_000_000)

    def test_metabolite_conversion_between_mass_and_concentration(self):
        mass = 50
        value = convert_measurement_units(200, 'g/L', 'mM', mass=mass)
        self.assertEqual(value, 4000)

        value = convert_measurement_units(200, 'mg/L', 'mM', mass=mass)
        self.assertEqual(value, 4)

        mass = 30
        value = convert_measurement_units(4000, 'mM', 'g/L', mass=mass)
        self.assertEqual(value, 120)
        value = convert_measurement_units(4000, 'mM', 'mg/L', mass=mass)
        self.assertEqual(value, 120_000)

        # Can't convert g/L without a mass
        value = convert_measurement_units(200, 'g/L', 'mM')
        self.assertIsNone(value)

        value = convert_measurement_units(3000, 'mM', 'g/L')
        self.assertIsNone(value)

    def test_time_conversion_to_the_same_unit(self):
        for t in (1, 0.3, 100.0, 0.5):
            for unit in ('d', 'h', 'm', 's'):
                self.assertEqual(convert_time(t, source=unit, target=unit), t)

    def test_time_conversion_to_seconds(self):
        for t in (1, 13, 100.0, 0.5):
            self.assertEqual(convert_time(t, source='m', target='s'), t * 60)
            self.assertEqual(convert_time(t, source='h', target='s'), t * 60 * 60)
            self.assertEqual(convert_time(t, source='d', target='s'), t * 24 * 60 * 60)

    def test_time_conversion_down(self):
        self.assertEqual(convert_time(1, source='d', target='h'), 24)
        self.assertEqual(convert_time(1, source='h', target='m'), 60)
        self.assertEqual(convert_time(0.5, source='h', target='m'), 30)

    def test_time_conversion_up(self):
        for t in (1, 13, 100.0, 0.5):
            self.assertEqual(convert_time(t * 60,           target='m', source='s'), t)
            self.assertEqual(convert_time(t * 60 * 60,      target='h', source='s'), t)
            self.assertEqual(convert_time(t * 24 * 60 * 60, target='d', source='s'), t)

    def test_time_conversion_rounding(self):
        self.assertEqual(convert_time(3600, source='s', target='h'), 1)
        self.assertEqual(convert_time(5400, source='s', target='h'), 1.5)

        # Rounded to 2 decimals after the dot
        self.assertEqual(convert_time(3500, source='s', target='h'), 0.97)

    def test_time_conversion_unknown_units(self):
        with self.assertRaises(ValueError): convert_time(1, source='s', target='unknown')
        with self.assertRaises(ValueError): convert_time(1, target='s', source='unknown')


if __name__ == '__main__':
    unittest.main()
