"""Reusable laboratory calculations for SciMantra Research Tools.

These functions mirror the generic calculations already exposed by the
Streamlit laboratory section. They provide a single tested home for formulas
as the UI is progressively modularized.
"""

import math


def molarity_from_mass(mass_g, molecular_weight_g_mol, volume_l):
    """Return molarity in mol/L from solute mass, molecular weight and volume."""
    if molecular_weight_g_mol <= 0 or volume_l <= 0:
        raise ValueError("Molecular weight and volume must be greater than zero.")
    return mass_g / molecular_weight_g_mol / volume_l


def dilution_stock_volume(c1, c2, v2):
    """Return stock volume V1 using C1*V1 = C2*V2."""
    if c1 <= 0:
        raise ValueError("Stock concentration C1 must be greater than zero.")
    if c2 < 0 or v2 <= 0:
        raise ValueError("Final concentration must be non-negative and V2 must be positive.")
    return c2 * v2 / c1


def solution_percentage(amount, total):
    """Return percentage concentration for a matching amount/total basis."""
    if total <= 0:
        raise ValueError("Total amount or volume must be greater than zero.")
    return amount / total * 100.0


def normality_from_molarity(molarity_value, n_factor):
    """Return normality from molarity and the reaction-specific n-factor."""
    if n_factor <= 0:
        raise ValueError("n-factor must be greater than zero.")
    return molarity_value * n_factor


def cfu_per_ml(colonies, reciprocal_dilution, plated_volume_ml):
    """Return CFU/mL from colony count, reciprocal dilution and plated volume."""
    if plated_volume_ml <= 0 or reciprocal_dilution <= 0:
        raise ValueError("Dilution and plated volume must be greater than zero.")
    return colonies * reciprocal_dilution / plated_volume_ml


def biomass_concentration(dry_biomass_g, culture_volume_l):
    """Return biomass concentration in g/L."""
    if culture_volume_l <= 0:
        raise ValueError("Culture volume must be greater than zero.")
    return dry_biomass_g / culture_volume_l


def growth_rate(x1, x2, t1, t2):
    """Return average growth rate (x2-x1)/(t2-t1)."""
    if t2 == t1:
        raise ValueError("Time points must be different.")
    return (x2 - x1) / (t2 - t1)


def specific_growth_rate(x1, x2, delta_t):
    """Return specific growth rate ln(X2/X1)/delta_t."""
    if x1 <= 0 or x2 <= 0 or delta_t <= 0:
        raise ValueError("X1, X2 and elapsed time must be greater than zero.")
    return math.log(x2 / x1) / delta_t


def bod_approx(initial_do, final_do, sample_volume_ml, bottle_volume_ml):
    """Return the simple dilution-adjusted BOD approximation used by the app."""
    if sample_volume_ml <= 0:
        raise ValueError("Sample volume must be greater than zero.")
    return (initial_do - final_do) * bottle_volume_ml / sample_volume_ml


def cod_from_titration(blank_ml, sample_ml, titrant_normality, sample_volume_ml):
    """Return COD in mg/L using the current app's 8000 conversion factor."""
    if sample_volume_ml <= 0 or titrant_normality <= 0:
        raise ValueError("Sample volume and titrant normality must be greater than zero.")
    return (blank_ml - sample_ml) * titrant_normality * 8000 / sample_volume_ml
