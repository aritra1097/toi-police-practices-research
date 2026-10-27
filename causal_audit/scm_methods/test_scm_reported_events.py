"""Synthetic fixtures only. They are never included as substantive observations."""
import argparse
import calendar
import csv
import datetime as dt
import tempfile
import unittest
from pathlib import Path

import numpy as np

from scm_reported_events import extreme, fit_compatible_set, read_panel, run, months_between, reported_weight_bound


class SyntheticControlTests(unittest.TestCase):
    def test_only_numerical_weight_bound_violations_are_clipped(self):
        self.assertEqual(reported_weight_bound(-1.033e-8), 0.)
        self.assertEqual(reported_weight_bound(1. + 1.033e-8), 1.)
        self.assertEqual(reported_weight_bound(.25), .25)
        with self.assertRaises(ValueError): reported_weight_bound(-.01)
        with self.assertRaises(ValueError): reported_weight_bound(1.01)

    def test_zero_preperiod_does_not_identify_weights_or_post_counterfactual(self):
        fit = fit_compatible_set(np.zeros(6), np.zeros((6, 3)))
        for index in range(3):
            lo, _ = extreme(fit, np.eye(3)[index])
            hi, _ = extreme(fit, np.eye(3)[index], True)
            self.assertAlmostEqual(lo, 0.)
            self.assertAlmostEqual(hi, 1.)
        lo, _ = extreme(fit, np.array([0., 2., 7.]))
        hi, _ = extreme(fit, np.array([0., 2., 7.]), True)
        self.assertAlmostEqual(lo, 0.)
        self.assertAlmostEqual(hi, 7.)
        np.testing.assert_allclose(fit['weights'], np.ones(3) / 3, atol=1e-6)

    def test_known_unique_convex_match(self):
        x = np.array([[1., 0., 0.], [0., 1., 0.], [0., 0., 1.], [2., 3., 4.]])
        truth = np.array([.2, .3, .5])
        fit = fit_compatible_set(x @ truth, x)
        self.assertLess(fit['minimum_max_pre_residual'], 1e-7)
        np.testing.assert_allclose(fit['weights'], truth, atol=1e-6)
        for index in range(3):
            lo, _ = extreme(fit, np.eye(3)[index])
            hi, _ = extreme(fit, np.eye(3)[index], True)
            self.assertLess(hi - lo, 1e-6)

    def test_joint_post_range_and_positive_minimax_error(self):
        # Each post-month can be zero, but no single weights make both zero.
        flat = fit_compatible_set(np.zeros(3), np.zeros((3, 2)))
        first = np.array([0., 2.])
        second = np.array([2., 0.])
        self.assertAlmostEqual(extreme(flat, first)[0], 0.)
        self.assertAlmostEqual(extreme(flat, second)[0], 0.)
        self.assertAlmostEqual(extreme(flat, (first + second) / 2)[0], 1.)
        self.assertAlmostEqual(extreme(flat, (first + second) / 2, True)[0], 1.)
        # A treated outcome outside the donors' hull needs positive pre-error.
        fit = fit_compatible_set(np.array([2., 2.]), np.array([[0., 1.], [0., 1.]]), slack=.5)
        self.assertAlmostEqual(fit['minimum_max_pre_residual'], 1.)
        self.assertAlmostEqual(extreme(fit, np.array([0., 1.]))[0], .5, places=6)
        self.assertAlmostEqual(extreme(fit, np.array([0., 1.]), True)[0], 1.)

    def write_fixture(self, path, unknown=False, post_change=0):
        fields = ['state', 'month', 'outcome', 'count', 'observed',
                  'complete_frame', 'eligible_days', 'unresolved_count']
        with path.open('w', newline='') as handle:
            writer = csv.DictWriter(handle, fieldnames=fields)
            writer.writeheader()
            for month in months_between(dt.date(2026, 1, 1), dt.date(2026, 10, 1)):
                for index, state in enumerate(['WB', 'KL', 'TN', 'TG']):
                    writer.writerow(dict(state=state, month=month.isoformat()[:7], outcome='fixture_only',
                        count=(index + post_change) if month >= dt.date(2026, 6, 1) else 0,
                        observed='false' if unknown and state == 'KL' and month.month == 3 else 'true',
                        complete_frame='true', eligible_days=27 if month.month == 10 else calendar.monthrange(2026, month.month)[1],
                        unresolved_count=0))

    def test_unknown_gate_and_complete_end_to_end(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'synthetic_fixture.csv'
            self.write_fixture(path, unknown=True)
            with self.assertRaisesRegex(ValueError, 'Unknown/incomplete'):
                read_panel(path, 'fixture_only', ['WB', 'KL', 'TN', 'TG'],
                           dt.date(2026, 1, 1), dt.date(2026, 10, 27), 'per30days')
            self.write_fixture(path)
            args = argparse.Namespace(input=str(path), output=str(Path(directory) / 'fixture_output'),
                outcome='fixture_only', treated='WB', donors=['KL', 'TN', 'TG'], start='2026-01',
                end='2026-10-27', scale='per30days', pre_slack=0., ridge=1e-6, no_plot=True)
            first = run(args)
            self.assertTrue(first['weight_set_nonunique'])
            self.assertEqual(first['post_eligible_days'], 149)
            self.assertEqual(first['pre_months'], 4)
            self.assertEqual(first['post_months'], 5)
            self.assertGreater(first['pooled_post_compatible_max_synthetic'], first['pooled_post_compatible_min_synthetic'])
            self.write_fixture(path, post_change=100)
            args.output = str(Path(directory) / 'fixture_changed_output')
            second = run(args)
            self.assertEqual(first['central_weights'], second['central_weights'])
            self.assertEqual(first['allowed_max_pre_residual'], second['allowed_max_pre_residual'])


if __name__ == '__main__':
    unittest.main()
