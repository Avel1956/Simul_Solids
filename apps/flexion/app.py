import streamlit as st
from apps.flexion.flexion_calculator import calculate_flexion
from apps.flexion.flexion_visualizer import visualize_flexion

def main():
    st.title("‿ Simulador de flexión pura")
    st.write("Esta aplicación calcula flexión pura en distintos casos.")

    moment = st.number_input("Momento flexor (Nm)", value=1000.0)
    area_moment_of_inertia = st.number_input("Momento de inercia de área (m^4)", value=0.0001)
    distance_from_neutral_axis = st.number_input("Distancia desde el eje neutral (m)", value=0.01)
    beam_length = st.number_input("Longitud de la viga (m)", value=1.0)

    st.header("Ecuaciones relevantes")
    st.latex(r"\sigma = \frac{M \cdot y}{I}")

    if st.button("Calcular esfuerzo de flexión"):
        stress = calculate_flexion(moment, area_moment_of_inertia, distance_from_neutral_axis)
        st.write(f"Esfuerzo de flexión: {stress:.2f} Pa")

        st.header("Solución paso a paso")
        st.subheader("Paso 1: Valores dados")
        st.write(f"M = {moment} Nm (Momento flexor)")
        st.write(f"I = {area_moment_of_inertia} m\u00b4 (Momento de inercia de área)")
        st.write(f"y = {distance_from_neutral_axis} m (Distancia desde el eje neutral)")

        st.subheader("Paso 2: Fórmula de flexión")
        st.latex(r"\sigma = \frac{M \cdot y}{I}")

        st.subheader("Paso 3: Sustituir valores")
        st.latex(r"\sigma = \frac{" + f"{moment:.1f}" + r" \cdot " + f"{distance_from_neutral_axis}" + "}{" + f"{area_moment_of_inertia}" + "}")

        st.subheader("Paso 4: Calcular")
        if stress >= 1000:
            st.latex(f"\sigma = {stress:.2f} \; \mathrm{{Pa}} = {stress/1000:.2f} \; \mathrm{{kPa}}")
        else:
            st.latex(f"\sigma = {stress:.2f} \; \mathrm{{Pa}}")

        st.header("Visualización del esfuerzo de flexión")
        fig = visualize_flexion(moment, area_moment_of_inertia, beam_length)
        st.pyplot(fig)

if __name__ == "__main__":
    main()
