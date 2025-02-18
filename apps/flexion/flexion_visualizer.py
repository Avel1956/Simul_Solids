import matplotlib.pyplot as plt
import numpy as np

def visualize_flexion(moment, area_moment_of_inertia, beam_length, num_points=100):
    """
    Visualizes the bending stress distribution along a beam under pure flexion.

    Args:
        moment (float): Bending moment (Nm).
        area_moment_of_inertia (float): Area moment of inertia (m^4).
        beam_length (float): Length of the beam (m).
        num_points (int): Number of points to discretize the beam for visualization.
    """
    x = np.linspace(-beam_length / 2, beam_length / 2, num_points)  # Beam length centered at 0
    stress = (moment * x) / area_moment_of_inertia  # Bending stress calculation

    plt.figure(figsize=(10, 6))
    plt.plot(x, stress)
    plt.xlabel("Distancia al eje neutral (m)")
    plt.ylabel("Esfuerzo de flexión (Pa)")
    plt.title("Distribucion del esfuerzo flector en flexión pura")
    plt.grid(True)
    return plt.gcf()  # Return the figure

if __name__ == '__main__':
    # Example usage:
    moment = 1000  # Nm
    area_moment_of_inertia = 0.0001  # m^4
    beam_length = 1  # m
    fig = visualize_flexion(moment, area_moment_of_inertia, beam_length)
    plt.show()
