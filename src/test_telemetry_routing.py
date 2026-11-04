"""
IdleBin Telemetry & Route Optimization Verification Suite
Automated regression tests for ultrasonic sensor filtering, outlier rejection,
and 2-opt municipal collection route planning.
"""

import unittest
from data_manager import AdaptiveUltrasonicFilter, DataManager
from route_optimizer import RouteOptimizer


class TestAdaptiveUltrasonicFilter(unittest.TestCase):
    def setUp(self):
        self.filter = AdaptiveUltrasonicFilter(
            window_size=5,
            max_deviation_cm=25.0,
            bin_depth_cm=80.0,
            sensor_offset_cm=5.0
        )
        self.bin_id = "TEST-IB-001"

    def test_single_reading_initialization(self):
        """Single initial pulse should populate baseline with default confidence."""
        res = self.filter.filter_reading(self.bin_id, 20.0)
        self.assertEqual(res["filtered_distance_cm"], 20.0)
        self.assertFalse(res["is_outlier"])
        self.assertEqual(res["sample_count"], 1)
        self.assertGreaterEqual(res["confidence_score"], 0.8)

    def test_outlier_spike_rejection(self):
        """High-amplitude acoustic reflection transient should be tagged as outlier and damped."""
        # Establish stable 20cm baseline
        for _ in range(4):
            self.filter.filter_reading(self.bin_id, 20.0)

        # Inject sudden echo spike (e.g. 68cm due to acoustic flutter)
        res = self.filter.filter_reading(self.bin_id, 68.0)
        self.assertTrue(res["is_outlier"])
        # Filtered distance should be significantly damped below the raw 68cm spike
        self.assertLess(res["filtered_distance_cm"], 45.0)

    def test_fill_percentage_boundaries(self):
        """Verify 0% and 100% boundary clamping."""
        # Full bin (distance <= sensor offset)
        full_res = self.filter.filter_reading("FULL-BIN", 4.0)
        self.assertEqual(full_res["fill_pct"], 100.0)

        # Empty bin (distance >= bin depth)
        empty_res = self.filter.filter_reading("EMPTY-BIN", 85.0)
        self.assertEqual(empty_res["fill_pct"], 0.0)

    def test_reset_clears_history(self):
        """Emptying a bin should flush historical rolling median."""
        for _ in range(5):
            self.filter.filter_reading(self.bin_id, 15.0)
        self.filter.reset_bin(self.bin_id)
        self.assertNotIn(self.bin_id, self.filter._history)


class TestRouteOptimizer(unittest.TestCase):
    def setUp(self):
        self.sample_bins = [
            {
                "id": "B-01",
                "name": "Point Alpha",
                "lat": 13.0310,
                "lng": 80.1810,
                "fill_pct": 92.0,
                "predicted_overflow_hrs": 0.5
            },
            {
                "id": "B-02",
                "name": "Point Beta",
                "lat": 13.0335,
                "lng": 80.1780,
                "fill_pct": 88.0,
                "predicted_overflow_hrs": 1.2
            },
            {
                "id": "B-03",
                "name": "Point Gamma",
                "lat": 13.0240,
                "lng": 80.1890,
                "fill_pct": 35.0,
                "predicted_overflow_hrs": 14.0
            }
        ]

    def test_haversine_positive_distance(self):
        """Distance between different points should be strictly positive."""
        dist = RouteOptimizer.haversine_distance_km(13.0310, 80.1810, 13.0335, 80.1780)
        self.assertGreater(dist, 0.2)
        self.assertLess(dist, 1.0)

    def test_two_opt_never_worsens_distance(self):
        """2-opt local search must yield an equal or shorter tour."""
        depot = RouteOptimizer.CAMPUS_DEPOT
        initial_seq = [depot] + self.sample_bins + [depot]
        initial_dist = RouteOptimizer.calculate_route_distance(initial_seq)
        optimized_seq = RouteOptimizer.two_opt_optimize(initial_seq)
        optimized_dist = RouteOptimizer.calculate_route_distance(optimized_seq)
        self.assertLessEqual(optimized_dist, initial_dist + 1e-6)

    def test_solve_route_critical_filtering(self):
        """Dynamic route should only include bins >= threshold (75%) or overflow <= 2 hrs."""
        result = RouteOptimizer.solve_route(self.sample_bins, threshold_fill_pct=75.0)
        self.assertEqual(result["dynamic_stops_count"], 2)
        self.assertGreater(result["diesel_saved_l"], 0.0)
        self.assertGreater(result["co2_avoided_kg"], 0.0)
        self.assertAlmostEqual(result["co2_avoided_kg"], round(result["diesel_saved_l"] * 2.68, 2), delta=0.05)


if __name__ == "__main__":
    unittest.main()
