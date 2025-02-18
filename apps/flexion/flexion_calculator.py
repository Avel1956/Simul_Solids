def calculate_flexion(moment, area_moment_of_inertia, distance_from_neutral_axis):
    """
    Calculates the bending stress due to pure flexion.

    Args:
        moment (float): Bending moment (Nm).
        area_moment_of_inertia (float): Area moment of inertia (m^4).
        distance_from_neutral_axis (float): Distance from the neutral axis to the point where stress is calculated (m).

    Returns:
        float: Bending stress (Pa).
    """
    try:
        stress = (moment * distance_from_neutral_axis) / area_moment_of_inertia
        return stress
    except ZeroDivisionError:
        return 0  # Avoid division by zero
