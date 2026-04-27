"""Preliminary Savitsky-inspired model for planing hulls.

This module provides a first, simplified implementation intended as a clean
starting point for NavalForge's hydrodynamics capabilities.

Important:
- This is NOT a full Savitsky method implementation.
- Equations are intentionally simplified and documented for transparency.
- TODO markers indicate where a complete Savitsky solver should be added.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import math


@dataclass(slots=True)
class PlaningHullInput:
    """Input data for preliminary planing hull assessment.

    All dimensions are SI except speed, which is given in knots.
    """

    length_m: float
    beam_m: float
    displacement_kg: float
    deadrise_deg: float
    speed_knots: float
    lcg_from_transom_m: float
    water_density_kg_m3: float = 1025.0
    gravity_m_s2: float = 9.80665


@dataclass(slots=True)
class SavitskyResult:
    """Output from the preliminary hydrodynamic calculation.

    Values are indicative and should not be used as final design data.
    """

    speed_ms: float
    froude_number: float
    resistance_n: float
    effective_power_kw: float
    trim_deg: float
    wetted_length_m: float
    lift_coefficient: float
    warnings: list[str] = field(default_factory=list)


class SavitskyModel:
    """Simplified planing hull model inspired by Savitsky.

    This class intentionally keeps the implementation simple and readable.
    A complete Savitsky method should eventually replace core approximations
    in `compute`.
    """

    def knots_to_ms(self, speed_knots: float) -> float:
        """Convert speed from knots to meters per second."""
        return speed_knots * 0.514444

    def estimate_power_kw(self, resistance_n: float, speed_ms: float) -> float:
        """Estimate effective power in kW from resistance and speed."""
        return (resistance_n * speed_ms) / 1000.0

    def validate_input(self, input_data: PlaningHullInput) -> list[str]:
        """Validate input and return non-fatal warnings.

        Raises:
            ValueError: if any required field is out of accepted bounds.
        """
        warnings: list[str] = []

        if input_data.length_m <= 0:
            raise ValueError("length_m must be greater than 0.")
        if input_data.beam_m <= 0:
            raise ValueError("beam_m must be greater than 0.")
        if input_data.displacement_kg <= 0:
            raise ValueError("displacement_kg must be greater than 0.")
        if input_data.speed_knots <= 0:
            raise ValueError("speed_knots must be greater than 0.")
        if not (0 <= input_data.deadrise_deg <= 35):
            raise ValueError("deadrise_deg must be between 0 and 35 degrees.")
        if not (0 <= input_data.lcg_from_transom_m <= input_data.length_m):
            raise ValueError("lcg_from_transom_m must be within hull length.")

        if input_data.speed_knots < 10:
            warnings.append(
                "Speed is below 10 knots; planing assumptions may not hold well."
            )

        length_beam_ratio = input_data.length_m / input_data.beam_m
        if not (2.0 <= length_beam_ratio <= 6.0):
            warnings.append(
                "Length/beam ratio is outside preliminary recommended range (2.0-6.0)."
            )

        return warnings

    def compute(self, input_data: PlaningHullInput) -> SavitskyResult:
        """Compute preliminary resistance, power, trim and wetted length.

        This is a simplified engineering estimate, not a complete Savitsky
        solution. It is suitable for early-stage concept iteration only.

        TODO:
            Replace simplified trim/wetted-length/drag approximations with
            a full iterative Savitsky formulation.
        """
        warnings = self.validate_input(input_data)

        speed_ms = self.knots_to_ms(input_data.speed_knots)
        g = input_data.gravity_m_s2
        rho = input_data.water_density_kg_m3

        froude_number = speed_ms / math.sqrt(g * input_data.length_m)

        displacement_weight_n = input_data.displacement_kg * g
        dynamic_pressure = 0.5 * rho * speed_ms * speed_ms

        lift_coefficient = displacement_weight_n / (dynamic_pressure * input_data.beam_m**2)

        # Simplified trim estimate in degrees:
        # - increases with lift coefficient
        # - slightly increases with deadrise
        # - bounded to typical planing range for preliminary use
        trim_estimate = 2.0 + 6.0 * min(max(lift_coefficient / 0.12, 0.0), 1.0)
        trim_estimate += 0.03 * input_data.deadrise_deg
        trim_deg = min(8.0, max(2.0, trim_estimate))

        # Simplified wetted-length estimate:
        # scales with beam and is reduced as lift coefficient grows.
        # includes a mild trim influence.
        cl_factor = 1.0 / (1.0 + 6.0 * lift_coefficient)
        trim_factor = 1.0 + 0.04 * (trim_deg - 4.0)
        wetted_length_m = input_data.beam_m * (1.8 + 3.2 * cl_factor) * trim_factor
        wetted_length_m = min(input_data.length_m, max(0.5 * input_data.beam_m, wetted_length_m))

        wetted_area_m2 = input_data.beam_m * wetted_length_m

        # Preliminary drag coefficient: baseline + deadrise + trim contribution.
        deadrise_rad = math.radians(input_data.deadrise_deg)
        drag_coefficient = 0.0045 + 0.0015 * math.sin(deadrise_rad) + 0.0008 * trim_deg

        resistance_n = dynamic_pressure * wetted_area_m2 * drag_coefficient
        effective_power_kw = self.estimate_power_kw(resistance_n, speed_ms)

        return SavitskyResult(
            speed_ms=speed_ms,
            froude_number=froude_number,
            resistance_n=resistance_n,
            effective_power_kw=effective_power_kw,
            trim_deg=trim_deg,
            wetted_length_m=wetted_length_m,
            lift_coefficient=lift_coefficient,
            warnings=warnings,
        )
