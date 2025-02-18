import streamlit as st
import numpy as np
from apps.indeterminacion.indeterminacion_calculator import IndeterminacionCalculator, CableParameters, MaterialProperties
from apps.indeterminacion.indeterminacion_visualizer import IndeterminacionVisualizer

def format_scientific(value: float, unit: str) -> str:
    """Formatea un valor científico con unidades."""
    if abs(value) < 0.001 or abs(value) > 1000:
        return f"{value:.2e} {unit}"
    return f"{value:.3f} {unit}"

def render_indeterminacion_app():
    # Inicializar calculadora y visualizador
    if 'indeterminacion_calculator' not in st.session_state:
        st.session_state.indeterminacion_calculator = IndeterminacionCalculator()
    if 'indeterminacion_visualizer' not in st.session_state:
        st.session_state.indeterminacion_visualizer = IndeterminacionVisualizer()
    
    calculator = st.session_state.indeterminacion_calculator
    visualizer = st.session_state.indeterminacion_visualizer
    
    # Título
    st.title("🔗 Análisis de Fuerzas en Cables")
    st.markdown("""
    Esta aplicación analiza la distribución de fuerzas en un sistema de dos cables que soportan una barra rígida.
    Permite calcular las fuerzas en cada cable y visualizar la deformación del sistema.
    """)
    
    # Layout de dos columnas
    col1, col2 = st.columns([1, 2])
    
    # Panel de entrada (columna izquierda)
    with col1:
        st.subheader("Parámetros de Entrada")
        
        # Botón para generar ejemplo aleatorio
        if st.button("Generar Ejemplo Aleatorio", key='random'):
            cable1, cable2, load = calculator.generate_random_example()
            st.session_state.update({
                'material1': 'Acero',
                'area1': cable1.A * 1e6,  # Convertir a mm²
                'length1': cable1.L,
                'material2': 'Acero',
                'area2': cable2.A * 1e6,
                'length2': cable2.L,
                'load': load
            })
            st.rerun()
        
        # Cable 1
        with st.expander("Cable 1", expanded=True):
            material1 = st.selectbox(
                "Material",
                ["Acero", "Aluminio", "Titanio", "Personalizado"],
                key='material1',
                help="Selecciona el material del cable 1"
            )
            
            if material1 == "Personalizado":
                E1 = st.number_input(
                    "Módulo de Young (GPa)",
                    min_value=1.0,
                    value=200.0,
                    key='custom_E1',
                    help="Módulo de elasticidad del material"
                ) * 1e9
            else:
                E1 = calculator.materials[material1]
            
            area1 = st.number_input(
                "Área (mm²)",
                min_value=1.0,
                value=100.0,
                key='area1',
                help="Área de la sección transversal del cable"
            )
            
            length1 = st.number_input(
                "Longitud (m)",
                min_value=0.1,
                value=2.0,
                key='length1',
                help="Longitud total del cable"
            )
        
        # Cable 2
        with st.expander("Cable 2", expanded=True):
            material2 = st.selectbox(
                "Material",
                ["Acero", "Aluminio", "Titanio", "Personalizado"],
                key='material2',
                help="Selecciona el material del cable 2"
            )
            
            if material2 == "Personalizado":
                E2 = st.number_input(
                    "Módulo de Young (GPa)",
                    min_value=1.0,
                    value=200.0,
                    key='custom_E2',
                    help="Módulo de elasticidad del material"
                ) * 1e9
            else:
                E2 = calculator.materials[material2]
            
            area2 = st.number_input(
                "Área (mm²)",
                min_value=1.0,
                value=100.0,
                key='area2',
                help="Área de la sección transversal del cable"
            )
            
            length2 = st.number_input(
                "Longitud (m)",
                min_value=0.1,
                value=2.0,
                key='length2',
                help="Longitud total del cable"
            )
        
        # Carga
        with st.expander("Carga", expanded=True):
            load = st.number_input(
                "Carga (N)",
                min_value=1.0,
                value=10000.0,
                key='load',
                help="Fuerza aplicada en el centro de la barra"
            )
    
    # Panel de visualización y resultados (columna derecha)
    with col2:
        try:
            # Crear objetos CableParameters
            cable1_params = CableParameters(
                E=E1,
                A=area1 * 1e-6,  # Convertir mm² a m²
                L=length1
            )
            
            cable2_params = CableParameters(
                E=E2,
                A=area2 * 1e-6,  # Convertir mm² a m²
                L=length2
            )
            
            # Calcular resultados
            results = calculator.calculate_forces(cable1_params, cable2_params, load)
            
            # Mostrar visualización
            fig = visualizer.create_figure(length1, length2, load, results)
            st.pyplot(fig)
            
            # Mostrar resultados
            st.subheader("Resultados")
            col_res1, col_res2 = st.columns(2)
            
            with col_res1:
                st.metric(
                    "Fuerza en Cable 1",
                    f"{results['F1']:.1f} N ({results['F1_percentage']:.1f}%)"
                )
                st.metric(
                    "Deformación Cable 1",
                    f"{results['delta1']*1000:.2f} mm"
                )
            
            with col_res2:
                st.metric(
                    "Fuerza en Cable 2",
                    f"{results['F2']:.1f} N ({results['F2_percentage']:.1f}%)"
                )
                st.metric(
                    "Deformación Cable 2",
                    f"{results['delta2']*1000:.2f} mm"
                )
            
            # Mostrar solución paso a paso
            st.subheader("Proceso de Solución")
            steps = calculator.generate_solution_steps(
                cable1_params, cable2_params, load, results
            )
            
            for step in steps:
                with st.expander(step["title"], expanded=False):
                    st.markdown(step["content"])
                    st.latex(step["equation"])
            
            # Teoría
            with st.expander("Teoría", expanded=False):
                st.markdown("""
                Este problema involucra el análisis de una barra rígida sostenida por dos cables con diferentes propiedades.
                La solución requiere aplicar:
                
                1. **Equilibrio de Fuerzas**
                   - La suma de fuerzas verticales debe ser cero
                   - F₁ + F₂ = P
                
                2. **Ley de Hooke**
                   - Relaciona la fuerza con la deformación en cada cable
                   - σ = E · ε
                   - F = (AE∆L)/L
                
                3. **Compatibilidad de Deformaciones**
                   - Al ser una barra rígida, el desplazamiento vertical es igual para ambos cables
                   - ∆L₁ = ∆L₂
                   - F₁L₁/(E₁A₁) = F₂L₂/(E₂A₂)
                """)
        
        except Exception as e:
            st.error(f"Error en la simulación: {str(e)}")
            st.error("Por favor, verifique los parámetros de entrada.")

if __name__ == "__main__":
    render_indeterminacion_app()
