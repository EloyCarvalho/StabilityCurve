"""Demo script for the preliminary Savitsky-inspired model."""

from pathlib import Path
import sys

# Allow running this file directly from repository root without installation.
sys.path.append(str(Path(__file__).resolve().parents[1]))

from navalforge.hydrodynamics.savitsky import PlaningHullInput, SavitskyModel


def main() -> None:
    model = SavitskyModel()

    input_data = PlaningHullInput(
        length_m=8.0,
        beam_m=2.6,
        displacement_kg=2500.0,
        deadrise_deg=18.0,
        speed_knots=28.0,
        lcg_from_transom_m=3.2,
    )

    result = model.compute(input_data)

    print("=== NavalForge - Preliminary Planing Hull Estimate ===")
    print(f"Speed:              {result.speed_ms:.2f} m/s")
    print(f"Froude number:      {result.froude_number:.3f}")
    print(f"Trim:               {result.trim_deg:.2f} deg")
    print(f"Wetted length:      {result.wetted_length_m:.2f} m")
    print(f"Lift coefficient:   {result.lift_coefficient:.4f}")
    print(f"Resistance:         {result.resistance_n:.1f} N")
    print(f"Effective power:    {result.effective_power_kw:.1f} kW")

    if result.warnings:
        print("\nWarnings:")
        for message in result.warnings:
            print(f"- {message}")


if __name__ == "__main__":
    main()
