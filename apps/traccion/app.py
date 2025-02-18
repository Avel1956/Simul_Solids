import streamlit as st
import time
from apps.traccion.traccion_calculator import TraccionCalculator
from apps.traccion.traccion_visualizer import TraccionVisualizer

def render_traccion_app():
    # Inicializar calculadora y visualizador
    if 'traccion_calculator' not in st.session_state:
        st.session_state.traccion_calculator = TraccionCalculator()
    if 'traccion_visualizer' not in st.session_state:
        st.session_state.traccion_visualizer = TraccionVisualizer()
    if 'traccion_running' not in st.session_state:
        st.session_state.traccion_running = False
    
    calculator = st.session_state.traccion_calculator
    visualizer = st.session_state.traccion_visualizer
    
    # Título
    st.title("💪 Simulador de Ensayo de Tracción")
    st.markdown("""
    Esta aplicación simula el ensayo de tracción en diferentes materiales, 
    permitiendo visualizar y comparar sus curvas esfuerzo-deformación.
    """)
    
    # Layout de dos columnas
    col1, col2 = st.columns([1, 2])
    
    # Panel de control (columna izquierda)
    with col1:
        st.subheader("Control de Ensayo")
        
        # Selección de material
        material = st.selectbox(
            "Material",
            options=['acero', 'aluminio', 'cobre'],
            format_func=lambda x: x.capitalize()
        )
        
        # Propiedades del material seleccionado
        props = calculator.get_material_properties(material)
        
        with st.expander("Propiedades del Material", expanded=True):
            st.write(f"Módulo de elasticidad: {props['modulo_elasticidad']} GPa")
            st.write(f"Límite elástico: {props['limite_elastico']} MPa")
            st.write(f"Resistencia a la tracción: {props['resistencia_traccion']} MPa")
            st.write(f"Coeficiente de Poisson: {props['coef_poisson']}")
        
        # Controles de simulación
        col_ctrl1, col_ctrl2 = st.columns(2)
        
        with col_ctrl1:
            if st.button("▶ Iniciar" if not st.session_state.traccion_running else "⏸ Pausar"):
                st.session_state.traccion_running = not st.session_state.traccion_running
        
        with col_ctrl2:
            if st.button("⟲ Reiniciar"):
                calculator.reset_simulation()
                visualizer.reset_data(material)
                st.session_state.traccion_running = False
        
        if st.button("🗑 Limpiar Todo"):
            calculator.reset_simulation()
            visualizer.reset_data()
            st.session_state.traccion_running = False
    
    # Panel de visualización (columna derecha)
    with col2:
        # Crear contenedor para la gráfica
        plot_container = st.empty()
        
        # Actualizar simulación
        if st.session_state.traccion_running:
            strain = calculator.get_next_strain()
            if strain is not None:
                stress = calculator.calculate_stress_strain(material, strain)
                visualizer.update_data(material, strain, stress)
            else:
                st.session_state.traccion_running = False
        
        # Mostrar gráfica
        fig = visualizer.create_figure()
        plot_container.plotly_chart(fig, use_container_width=True)
        
        # Ecuaciones
        with st.expander("Ecuaciones Fundamentales"):
            st.latex(r"\sigma = E\varepsilon \quad \text{(Región elástica)}")
            st.latex(r"\sigma = \sigma_y + H\varepsilon_p \quad \text{(Región plástica)}")
            
            st.markdown("""
            Donde:
            - σ: Esfuerzo normal
            - E: Módulo de elasticidad
            - ε: Deformación unitaria
            - σ_y: Límite elástico
            - H: Factor de endurecimiento
            - ε_p: Deformación plástica
            """)
        
        # Rerun para actualización continua
        if st.session_state.traccion_running:
            time.sleep(0.1)  # Controlar velocidad de actualización
            st.rerun()
