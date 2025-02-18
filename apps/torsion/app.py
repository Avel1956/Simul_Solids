import streamlit as st
import numpy as np
from apps.torsion.torsion_calculator import TorsionCalculator
from apps.torsion.torsion_visualizer import TorsionVisualizer

def format_scientific(value: float, unit: str) -> str:
    """Formatea un valor científico con unidades."""
    if abs(value) < 0.001 or abs(value) > 1000:
        return f"{value:.2e} {unit}"
    return f"{value:.3f} {unit}"

def main():
    # Inicializar calculadora y visualizador
    if 'torsion_calculator' not in st.session_state:
        st.session_state.torsion_calculator = TorsionCalculator()
    if 'torsion_visualizer' not in st.session_state:
        st.session_state.torsion_visualizer = TorsionVisualizer()
    
    calculator = st.session_state.torsion_calculator
    visualizer = st.session_state.torsion_visualizer
    
    # Título
    st.title("💫 Simulador de Torsión")
    st.markdown("""
    Esta aplicación simula la deformación torsional en elementos cilíndricos, 
    permitiendo visualizar la distribución de esfuerzos y calcular parámetros clave.
    """)
    
    # Layout de dos columnas
    col1, col2 = st.columns([1, 2])
    
    # Panel de entrada (columna izquierda)
    with col1:
        st.subheader("Parámetros de Entrada")
        
        # Geometría
        with st.expander("Geometría", expanded=True):
            length = st.number_input("Longitud (m)", 
                                   min_value=0.1, 
                                   value=1.0, 
                                   step=0.1,
                                   key='length')
            outer_diameter = st.number_input("Diámetro exterior (m)", 
                                           min_value=0.01, 
                                           value=0.1, 
                                           step=0.01,
                                           key='outer_diameter')
            inner_diameter = st.number_input("Diámetro interior (m)", 
                                           min_value=0.0,
                                           max_value=outer_diameter-0.001, 
                                           value=0.0, 
                                           step=0.01,
                                           key='inner_diameter')
            segments = st.slider("Número de segmentos", 
                               min_value=4, 
                               max_value=50, 
                               value=20,
                               key='segments')
        
        # Material
        with st.expander("Material", expanded=True):
            elastic_modulus = st.number_input("Módulo de elasticidad (GPa)", 
                                            min_value=1.0, 
                                            value=200.0, 
                                            step=1.0,
                                            key='elastic_modulus')
            shear_modulus = st.number_input("Módulo de corte (GPa)", 
                                           min_value=1.0, 
                                           value=80.0, 
                                           step=1.0,
                                           key='shear_modulus')
            poisson_ratio = st.number_input("Coeficiente de Poisson", 
                                          min_value=0.0, 
                                          max_value=0.5, 
                                          value=0.3, 
                                          step=0.01,
                                          key='poisson_ratio')
        
        # Carga
        with st.expander("Carga", expanded=True):
            torque = st.number_input("Momento torsor (N⋅m)", 
                                   value=100.0, 
                                   step=10.0,
                                   key='torque')
        
        # Visualización
        with st.expander("Visualización", expanded=True):
            deformation_scale = st.slider("Escala de deformación", 
                                        min_value=0.0, 
                                        max_value=10.0, 
                                        value=1.0, 
                                        step=0.1,
                                        key='deformation_scale')
            
            show_original = st.checkbox("Mostrar estado original", 
                                      value=True,
                                      key='show_original')
            show_deformed = st.checkbox("Mostrar estado deformado", 
                                      value=True,
                                      key='show_deformed')
            show_stress = st.checkbox("Mostrar distribución de esfuerzos", 
                                    value=True,
                                    key='show_stress')
            show_grid = st.checkbox("Mostrar malla de referencia", 
                                  value=True,
                                  key='show_grid')
            show_wireframe = st.checkbox("Mostrar malla del modelo", 
                                       value=False,
                                       key='show_wireframe')
            
            if st.button("Reiniciar visualización", key='reset_btn'):
                st.session_state.deformation_scale = 1.0
                st.rerun()
    
    # Panel de visualización y resultados (columna derecha)
    with col2:
        try:
            # Preparar parámetros
            params = {
                'length': length,
                'outer_diameter': outer_diameter,
                'inner_diameter': inner_diameter,
                'segments': segments,
                'elastic_modulus': elastic_modulus,
                'shear_modulus': shear_modulus,
                'poisson_ratio': poisson_ratio,
                'torque': torque
            }
            
            # Actualizar opciones de visualización
            visualizer.set_visualization_options(
                show_original=show_original,
                show_deformed=show_deformed,
                show_stress=show_stress,
                show_grid=show_grid,
                show_wireframe=show_wireframe
            )
            visualizer.set_deformation_scale(deformation_scale)
            
            # Calcular resultados
            results = calculator.calculate_results(params)
            
            # Mostrar visualización 3D
            fig = visualizer.create_figure(params)
            st.plotly_chart(fig, use_container_width=True)
            
            # Mostrar resultados
            st.subheader("Resultados")
            col_res1, col_res2 = st.columns(2)
            
            with col_res1:
                st.metric(
                    "Momento polar de inercia", 
                    format_scientific(results['polar_moment_of_inertia'], "m⁴")
                )
                st.metric(
                    "Ángulo de torsión", 
                    format_scientific(results['twist_angle_degrees'], "°")
                )
                
            with col_res2:
                st.metric(
                    "Esfuerzo cortante máximo", 
                    format_scientific(results['max_shear_stress']/1e6, "MPa")
                )
            
            # Ecuaciones
            st.subheader("Ecuaciones Fundamentales")
            st.latex(r"\tau_{max} = \frac{Tr}{J}")
            st.latex(r"\theta = \frac{TL}{GJ}")
            st.latex(r"J = \frac{\pi}{32}(d_o^4 - d_i^4)")
            
            with st.expander("Leyenda de variables"):
                st.markdown("""
                - τ_max: Esfuerzo cortante máximo
                - T: Momento torsor
                - r: Radio exterior
                - J: Momento polar de inercia
                - θ: Ángulo de torsión
                - L: Longitud
                - G: Módulo de corte
                - d_o: Diámetro exterior
                - d_i: Diámetro interior
                """)
        except Exception as e:
            st.error(f"Error en la simulación: {str(e)}")
            st.error("Por favor, verifique los parámetros de entrada.")

if __name__ == "__main__":
    main()
