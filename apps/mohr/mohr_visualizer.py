import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

class MohrVisualizer:
    """
    Clase para visualizar el Círculo de Mohr y el elemento de esfuerzo.
    Proporciona métodos para crear gráficos interactivos que muestran
    el estado de esfuerzos y su transformación.
    """
    
    def __init__(self):
        """Inicializa el visualizador del Círculo de Mohr."""
        self.show_principal_stresses = True
        self.show_max_shear = True
        self.show_original_state = True
        self.show_transformed_state = True
        self.show_grid = True
        self.show_annotations = True
    
    def set_visualization_options(self, **options):
        """
        Configura las opciones de visualización.
        
        Args:
            **options: Opciones de visualización como pares clave-valor
        """
        if 'show_principal_stresses' in options:
            self.show_principal_stresses = options['show_principal_stresses']
        if 'show_max_shear' in options:
            self.show_max_shear = options['show_max_shear']
        if 'show_original_state' in options:
            self.show_original_state = options['show_original_state']
        if 'show_transformed_state' in options:
            self.show_transformed_state = options['show_transformed_state']
        if 'show_grid' in options:
            self.show_grid = options['show_grid']
        if 'show_annotations' in options:
            self.show_annotations = options['show_annotations']
    
    def create_figure(self, params, calculator):
        """
        Crea una figura con el Círculo de Mohr.
        
        Args:
            params (dict): Parámetros de entrada
            calculator (MohrCalculator): Instancia del calculador
            
        Returns:
            plotly.graph_objects.Figure: Figura con el círculo de Mohr
        """
        # Crear figura para el Círculo de Mohr
        fig = go.Figure()
        
        # Calcular resultados
        results = calculator.calculate_results(params)
        
        # Añadir Círculo de Mohr
        self._add_mohr_circle(fig, params, calculator, results)
        
        # Configurar layout
        fig.update_layout(
            height=600,
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            margin=dict(l=20, r=20, t=60, b=20)
        )
        
        return fig
    
    def _add_mohr_circle(self, fig, params, calculator, results):
        """
        Añade el Círculo de Mohr a la figura.
        
        Args:
            fig (plotly.graph_objects.Figure): Figura a la que añadir el círculo
            params (dict): Parámetros de entrada
            calculator (MohrCalculator): Instancia del calculador
            results (dict): Resultados calculados
        """
        # Extraer parámetros
        sigma_x = params.get('sigma_x', 0)
        sigma_y = params.get('sigma_y', 0)
        tau_xy = params.get('tau_xy', 0)
        theta = params.get('theta', 0)
        
        # Calcular puntos del círculo
        sigma_circle, tau_circle = calculator.calculate_circle_points(params)
        
        # Añadir círculo
        fig.add_trace(
            go.Scatter(
                x=sigma_circle,
                y=tau_circle,
                mode='lines',
                name='Círculo de Mohr',
                line=dict(color='blue', width=2)
            )
        )
        
        # Añadir punto para el estado original
        fig.add_trace(
            go.Scatter(
                x=[sigma_x, sigma_y],
                y=[tau_xy, -tau_xy],
                mode='markers+text',
                name='Estado Original',
                marker=dict(color='red', size=10),
                text=['(σx, τxy)', '(σy, -τxy)'],
                textposition='top center',
                visible=self.show_original_state
            )
        )
        
        # Añadir punto para el estado transformado
        if self.show_transformed_state and theta != 0:
            transformed = calculator.calculate_transformed_element(params, theta)
            fig.add_trace(
                go.Scatter(
                    x=[transformed['sigma_x'], transformed['sigma_y']],
                    y=[transformed['tau_xy'], -transformed['tau_xy']],
                    mode='markers+text',
                    name=f'Estado Rotado ({theta}°)',
                    marker=dict(color='green', size=10),
                    text=[f'(σx\', τxy\')', f'(σy\', -τxy\')'],
                    textposition='top center'
                )
            )
        
        # Añadir puntos para esfuerzos principales
        if self.show_principal_stresses:
            fig.add_trace(
                go.Scatter(
                    x=[results['sigma_1'], results['sigma_2']],
                    y=[0, 0],
                    mode='markers+text',
                    name='Esfuerzos Principales',
                    marker=dict(color='purple', size=10),
                    text=['σ1', 'σ2'],
                    textposition='top center'
                )
            )
        
        # Añadir puntos para esfuerzo cortante máximo
        if self.show_max_shear:
            center = results['center']
            fig.add_trace(
                go.Scatter(
                    x=[center, center],
                    y=[results['tau_max'], -results['tau_max']],
                    mode='markers+text',
                    name='Esfuerzo Cortante Máximo',
                    marker=dict(color='orange', size=10),
                    text=['τmax', '-τmax'],
                    textposition='top center'
                )
            )
        
        # Añadir línea de centro
        fig.add_trace(
            go.Scatter(
                x=[results['center'], results['center']],
                y=[-1.2*results['radius'], 1.2*results['radius']],
                mode='lines',
                name='Centro',
                line=dict(color='gray', width=1, dash='dash'),
                showlegend=False
            )
        )
        
        # Añadir eje x
        fig.add_trace(
            go.Scatter(
                x=[results['center']-1.2*results['radius'], results['center']+1.2*results['radius']],
                y=[0, 0],
                mode='lines',
                line=dict(color='black', width=1),
                showlegend=False
            )
        )
        
        # Configurar ejes para mantener el círculo circular
        radius = results['radius']
        center = results['center']
        margin = radius * 0.2  # 20% de margen
        
        # Configurar ejes
        fig.update_layout(
            xaxis=dict(
                title_text="Esfuerzo Normal σ (MPa)",
                zeroline=True,
                showgrid=self.show_grid,
                range=[center-radius-margin, center+radius+margin]
            ),
            yaxis=dict(
                title_text="Esfuerzo Cortante τ (MPa)",
                zeroline=True,
                showgrid=self.show_grid,
                range=[-radius-margin, radius+margin],
                scaleanchor="x",
                scaleratio=1
            )
        )
