import streamlit as st
from streamlit_extras.grid import grid

st.set_page_config(
    page_title="Simulaciones de Ingeniería",
    page_icon="🔧",
    layout="wide"
)

# Título y descripción
st.title("Mecánica de Sólidos")
st.markdown("""
Esta plataforma ofrece una colección de simulaciones interactivas para el análisis y 
visualización de diferentes fenómenos de Mecánica de Sólidos.
""")

# Crear grid para las aplicaciones
apps_grid = grid(3, vertical_align="top")

# Simulador de Tracción
with apps_grid.container():
    st.markdown("""
    ### 📈 Simulador de tracción
    
    Analiza los esfuerzos y deformaciones en elementos sometidos a tracción, visualiza la curva 
    esfuerzo-deformación y calcula parámetros clave.
    """)
    st.image("assets/traccion.png")
    if st.button("Abrir Simulador", key="traccion_btn"):
        st.switch_page("pages/2_Simulador_de_Traccion.py")

with apps_grid.container():
    st.markdown("""
    ### 🔗 Generador de Indeterminaciones
    
    Analiza la distribución de fuerzas en un sistema de dos cables que soportan una barra rígida.
    Calcula las fuerzas en cada cable y visualiza la deformación del sistema.
    """)
    st.image("assets/indeterminacion.png")
    if st.button("Abrir Simulador", key="indeterminacion_btn"):
        st.switch_page("pages/3_Generador_de_Indeterminaciones.py")

# Simulador de Torsión
with apps_grid.container():
    st.markdown("""
    ### 🌀 Simulador de Torsión
    
    Analiza la deformación torsional en elementos cilíndricos, visualiza la distribución 
    de esfuerzos y calcula parámetros clave.
    """)
    st.image("assets/torsion.png")
    if st.button("Abrir Simulador", key="torsion_btn"):
        st.switch_page("pages/1_Simulador_de_Torsion.py")

with apps_grid.container():
    st.markdown("""
    ### stream Simulador de Flexión pura
    
    Analiza los esfuerzos y deformaciones en elementos sometidos a flexión pura.
    """)
    st.image("assets/flexion.png")
    if st.button("Abrir Simulador", key="flexion_btn"):
        st.switch_page("pages/4_Simulador_de_Flexion.py")

with apps_grid.container():
    st.markdown("""
    ### ⭕ Simulador del Círculo de Mohr
    
    Analiza y visualiza la transformación de esfuerzos en un elemento,
    calcula esfuerzos principales y esfuerzo cortante máximo.
    """)
    st.image("assets/mohr.png")
    if st.button("Abrir Simulador", key="mohr_btn"):
        st.switch_page("pages/5_Simulador_de_Mohr.py")

# Footer
st.markdown("---")
st.markdown("Jaime Andrés Vélez, Universidad Javeriana de Cali- 2025")
