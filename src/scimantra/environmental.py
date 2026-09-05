"""Reusable environmental biotechnology calculations for SciMantra."""


def removal_efficiency(influent, effluent):
    """Return pollutant removal efficiency as a percentage."""
    if influent <= 0:
        raise ValueError("Influent concentration must be greater than zero.")
    return (influent - effluent) / influent * 100.0


def loading_rate(concentration, flow_rate):
    """Return concentration multiplied by flow rate in consistent units."""
    if concentration < 0 or flow_rate < 0:
        raise ValueError("Concentration and flow rate must be non-negative.")
    return concentration * flow_rate


def ebrt(reactor_volume, flow_rate):
    """Return empty-bed residence time (EBRT) as volume/flow."""
    if reactor_volume < 0:
        raise ValueError("Reactor volume must be non-negative.")
    if flow_rate <= 0:
        raise ValueError("Flow rate must be greater than zero.")
    return reactor_volume / flow_rate


def h2s_removal(inlet, outlet):
    """Return H2S removal percentage using inlet and outlet concentrations."""
    return removal_efficiency(inlet, outlet)
