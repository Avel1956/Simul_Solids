import streamlit as st
import numpy as np
from apps.mohr.mohr_calculator import MohrCalculator
from apps.mohr.mohr_visualizer import MohrVisualizer

def format_scientific(value: float, unit: str) -> str:
    """Formatea un valor científico con unidades."""
    if abs(value) < 0.001 or abs(value) > 1000:
        return f"{value:.2e} {unit}"
    return f"{value:.3f} {unit}"

def main():
    # Inicializar calculadora y visualizador
    if 'mohr_calculator' not in st.session_state:
        st.session_state.mohr_calculator = MohrCalculator()
    if 'mohr_visualizer' not in st.session_state:
        st.session_state.mohr_visualizer = MohrVisualizer()
    
    calculator = st.session_state.mohr_calculator
    visualizer = st.session_state.mohr_visualizer
    
    # Título
    st.title("⭕ Simulador del Círculo de Mohr")
    st.markdown("""
    Esta aplicación permite analizar y visualizar la transformación de esfuerzos en un elemento,
    calcular esfuerzos principales y esfuerzo cortante máximo.
    """)
    
    # Layout de dos columnas: panel de entrada y visualización
    col1, col2 = st.columns([1, 1.5])
    
    # Panel de entrada (columna izquierda)
    with col1:
        st.subheader("Parámetros de Entrada")
        
        # Estado de esfuerzos
        with st.expander("Estado de Esfuerzos", expanded=True):
            sigma_x = st.number_input("Esfuerzo normal σx (MPa)", 
                                    value=50.0, 
                                    step=10.0,
                                    key='sigma_x')
            sigma_y = st.number_input("Esfuerzo normal σy (MPa)", 
                                    value=-20.0, 
                                    step=10.0,
                                    key='sigma_y')
            tau_xy = st.number_input("Esfuerzo cortante τxy (MPa)", 
                                   value=30.0, 
                                   step=10.0,
                                   key='tau_xy')
        
        # Ángulo de rotación
        with st.expander("Transformación de Esfuerzos", expanded=True):
            theta = st.slider("Ángulo de rotación θ (grados)", 
                            min_value=-90, 
                            max_value=90, 
                            value=0,
                            step=5,
                            key='theta')
        
        # Visualización
        with st.expander("Visualización", expanded=True):
            show_principal_stresses = st.checkbox("Mostrar esfuerzos principales", 
                                               value=True,
                                               key='show_principal_stresses')
            show_max_shear = st.checkbox("Mostrar esfuerzo cortante máximo", 
                                       value=True,
                                       key='show_max_shear')
            show_original_state = st.checkbox("Mostrar estado original", 
                                           value=True,
                                           key='show_original_state')
            show_transformed_state = st.checkbox("Mostrar estado transformado", 
                                              value=True,
                                              key='show_transformed_state')
            show_grid = st.checkbox("Mostrar cuadrícula", 
                                  value=True,
                                  key='show_grid')
            show_annotations = st.checkbox("Mostrar anotaciones", 
                                        value=True,
                                        key='show_annotations')
            
            if st.button("Reiniciar visualización", key='reset_btn'):
                st.session_state.theta = 0
                st.session_state.show_principal_stresses = True
                st.session_state.show_max_shear = True
                st.session_state.show_original_state = True
                st.session_state.show_transformed_state = True
                st.session_state.show_grid = True
                st.session_state.show_annotations = True
                st.rerun()
    
    # Panel de visualización y resultados (columna derecha)
    with col2:
        try:
            # Preparar parámetros
            params = {
                'sigma_x': sigma_x,
                'sigma_y': sigma_y,
                'tau_xy': tau_xy,
                'theta': theta
            }
            
            # Actualizar opciones de visualización
            visualizer.set_visualization_options(
                show_principal_stresses=show_principal_stresses,
                show_max_shear=show_max_shear,
                show_original_state=show_original_state,
                show_transformed_state=show_transformed_state,
                show_grid=show_grid,
                show_annotations=show_annotations
            )
            
            # Calcular resultados
            results = calculator.calculate_results(params)
            
            # Mostrar visualización
            fig = visualizer.create_figure(params, calculator)
            st.plotly_chart(fig, use_container_width=True)
            
            # Mostrar resultados en una fila
            st.subheader("Resultados")
            cols = st.columns(4)
            
            cols[0].metric(
                "Esfuerzo principal σ₁", 
                format_scientific(results['sigma_1'], "MPa")
            )
            cols[1].metric(
                "Esfuerzo principal σ₂", 
                format_scientific(results['sigma_2'], "MPa")
            )
            cols[2].metric(
                "Esfuerzo cortante máximo τₘₐₓ", 
                format_scientific(results['tau_max'], "MPa")
            )
            cols[3].metric(
                "Ángulo principal θₚ", 
                format_scientific(results['theta_p'], "°")
            )
            
            # Ecuaciones en un expander
            with st.expander("Ecuaciones Fundamentales", expanded=False):
                st.latex(r"\sigma_x' = \frac{\sigma_x + \sigma_y}{2} + \frac{\sigma_x - \sigma_y}{2}\cos(2\theta) + \tau_{xy}\sin(2\theta)")
                st.latex(r"\sigma_y' = \frac{\sigma_x + \sigma_y}{2} - \frac{\sigma_x - \sigma_y}{2}\cos(2\theta) - \tau_{xy}\sin(2\theta)")
                st.latex(r"\tau_{xy}' = -\frac{\sigma_x - \sigma_y}{2}\sin(2\theta) + \tau_{xy}\cos(2\theta)")
                
                # Esfuerzos principales
                st.latex(r"\sigma_{1,2} = \frac{\sigma_x + \sigma_y}{2} \pm \sqrt{\left(\frac{\sigma_x - \sigma_y}{2}\right)^2 + \tau_{xy}^2}")
                st.latex(r"\tau_{max} = \sqrt{\left(\frac{\sigma_x - \sigma_y}{2}\right)^2 + \tau_{xy}^2}")
                st.latex(r"\theta_p = \frac{1}{2}\tan^{-1}\left(\frac{2\tau_{xy}}{\sigma_x - \sigma_y}\right)")
            
            with st.expander("Leyenda de variables"):
                st.markdown("""
                - σx, σy: Esfuerzos normales en las direcciones x e y
                - τxy: Esfuerzo cortante en el plano xy
                - σx', σy': Esfuerzos normales transformados
                - τxy': Esfuerzo cortante transformado
                - σ1, σ2: Esfuerzos principales
                - τmax: Esfuerzo cortante máximo
                - θ: Ángulo de rotación
                - θp: Ángulo principal
                """)
                
            # Información educativa
            with st.expander("Información sobre el Círculo de Mohr"):
                st.markdown("""
                ### ¿Qué es el Círculo de Mohr?
                
                El Círculo de Mohr es una representación gráfica bidimensional del estado de esfuerzos en un punto de un cuerpo. 
                Permite visualizar cómo los esfuerzos normales y cortantes varían con la orientación del elemento.
                
                ### Interpretación del Círculo
                
                - **Centro del círculo**: Representa el promedio de los esfuerzos normales (σx + σy)/2
                - **Radio del círculo**: Determina el esfuerzo cortante máximo
                - **Puntos en el círculo**: Cada punto representa un estado de esfuerzos para una orientación específica
                - **Esfuerzos principales**: Corresponden a los puntos donde el círculo intersecta el eje horizontal (τ = 0)
                
                ### Aplicaciones
                
                - Análisis de falla en materiales
                - Diseño de elementos estructurales
                - Análisis de concentración de esfuerzos
                - Determinación de planos críticos
                """)
                
        except Exception as e:
            st.error(f"Error en la simulación: {str(e)}")
            st.error("Por favor, verifique los parámetros de entrada.")

if __name__ == "__main__":
    main()
