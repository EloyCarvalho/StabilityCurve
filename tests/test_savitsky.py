"""Tests for preliminary Savitsky-inspired hydrodynamics model."""

import math
import unittest

from navalforge.hydrodynamics.savitsky import PlaningHullInput, SavitskyModel


class TestSavitskyModel(unittest.TestCase):
    def setUp(self) -> None:
        self.model = SavitskyModel()
        self.valid_input = PlaningHullInput(
            length_m=8.0,
            beam_m=2.6,
            displacement_kg=2500.0,
            deadrise_deg=18.0,
            speed_knots=28.0,
            lcg_from_transom_m=3.2,
        )

    def test_knots_to_ms_conversion(self) -> None:
        converted = self.model.knots_to_ms(10.0)
        self.assertTrue(math.isclose(converted, 5.14444, rel_tol=1e-6))

    def test_compute_returns_positive_resistance(self) -> None:
        result = self.model.compute(self.valid_input)
        self.assertGreater(result.resistance_n, 0.0)

    def test_compute_returns_positive_power(self) -> None:
        result = self.model.compute(self.valid_input)
        self.assertGreater(result.effective_power_kw, 0.0)

    def test_invalid_input_raises_value_error(self) -> None:
        invalid = PlaningHullInput(
            length_m=-8.0,
            beam_m=2.6,
            displacement_kg=2500.0,
            deadrise_deg=18.0,
            speed_knots=28.0,
            lcg_from_transom_m=3.2,
        )
        with self.assertRaises(ValueError):
            self.model.compute(invalid)

    def test_warning_for_low_speed(self) -> None:
        low_speed_input = PlaningHullInput(
            length_m=8.0,
            beam_m=2.6,
            displacement_kg=2500.0,
            deadrise_deg=18.0,
            speed_knots=8.0,
            lcg_from_transom_m=3.2,
        )
        result = self.model.compute(low_speed_input)
        self.assertTrue(any("below 10 knots" in w for w in result.warnings))


if __name__ == "__main__":
    unittest.main()
