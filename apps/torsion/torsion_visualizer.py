import numpy as np
import plotly.graph_objects as go
from typing import Dict, List, Tuple

class TorsionVisualizer:
    def __init__(self):
        self.show_original = True
        self.show_deformed = True
        self.show_stress = True
        self.show_grid = True
        self.show_wireframe = False
        self.deformation_scale = 1.0

    def create_cylinder_mesh(self, params: Dict, deformation: float = 0) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """
        Crea la malla del cilindro con deformación por torsión.
        
        Args:
            params: Diccionario con parámetros geométricos
            deformation: Factor de deformación
            
        Returns:
            Tupla de arrays (x, y, z, colors, angles) para la visualización
        """
        length = params['length']
        outer_diameter = params['outer_diameter']
        segments = params['segments']
        torque = params['torque']
        shear_modulus = params['shear_modulus'] * 1e9  # Convertir de GPa a Pa
        
        radius = outer_diameter / 2
        
        # Crear malla cilíndrica
        theta = np.linspace(0, 2*np.pi, 36)
        z = np.linspace(-length/2, length/2, segments)
        theta, z = np.meshgrid(theta, z)
        
        # Calcular altura relativa para la deformación
        height_ratio = (z - np.min(z)) / length

        # Coordenadas base
        x = radius * np.cos(theta)
        y = radius * np.sin(theta)

        # Calcular ángulos de torsión para cada segmento
        angles = np.zeros_like(z)
        if deformation != 0:
            # Calcular el ángulo de torsión real
            J = (np.pi / 32) * (outer_diameter**4 - params['inner_diameter']**4)
            max_angle = (torque * length) / (shear_modulus * J)
            
            # Aplicar la escala de deformación
            twist_angle = max_angle * deformation
            rotation = twist_angle * height_ratio

            x_twisted = x * np.cos(rotation) - y * np.sin(rotation)
            y_twisted = x * np.sin(rotation) + y * np.cos(rotation)
            
            x = x_twisted
            y = y_twisted
            angles = np.degrees(rotation)

        # Calcular colores basados en el esfuerzo cortante
        if deformation != 0:
            # τ = Tr/J
            colors = np.abs(torque * radius * height_ratio / J)
        else:
            colors = np.zeros_like(z)
        
        return x, y, z, colors, angles

    def create_figure(self, params: Dict) -> go.Figure:
        """
        Crea la figura 3D completa con todas las visualizaciones.
        
        Args:
            params: Diccionario con parámetros de la simulación
            
        Returns:
            Figura de Plotly
        """
        fig = go.Figure()

        # Crear malla original
        if self.show_original:
            x, y, z, _, _ = self.create_cylinder_mesh(params, 0)
            fig.add_trace(go.Surface(
                x=x, y=y, z=z,
                opacity=0.3,
                showscale=False,
                colorscale='Blues',
                name='Original'
            ))

        # Crear malla deformada
        if self.show_deformed:
            x, y, z, colors, angles = self.create_cylinder_mesh(params, self.deformation_scale)
            
            # Superficie principal
            fig.add_trace(go.Surface(
                x=x, y=y, z=z,
                surfacecolor=colors if self.show_stress else None,
                colorscale=[[0, 'blue'], [1, 'red']] if self.show_stress else 'Blues',
                showscale=self.show_stress,
                colorbar=dict(
                    title=dict(
                        text='Esfuerzo Cortante (Pa)',
                        side='right'
                    )
                ) if self.show_stress else None,
                name='Deformado'
            ))
            
            # Añadir wireframe si está activado
            if self.show_wireframe:
                for i in range(x.shape[0]):
                    fig.add_trace(go.Scatter3d(
                        x=x[i, :], y=y[i, :], z=z[i, :],
                        mode='lines',
                        line=dict(color='black', width=1),
                        showlegend=False
                    ))
                for j in range(x.shape[1]):
                    fig.add_trace(go.Scatter3d(
                        x=x[:, j], y=y[:, j], z=z[:, j],
                        mode='lines',
                        line=dict(color='black', width=1),
                        showlegend=False
                    ))

            # Añadir etiquetas de ángulo
            if self.deformation_scale > 0:
                for i in range(1, len(z)):
                    # Tomar un punto en el radio exterior para la etiqueta
                    angle = angles[i, 0]  # Tomar el ángulo del primer punto del segmento
                    if angle != 0:
                        fig.add_trace(go.Scatter3d(
                            x=[x[i, 0]],
                            y=[y[i, 0]],
                            z=[z[i, 0]],
                            mode='text',
                            text=[f'{angle:.3f}°'],
                            textposition='middle right',
                            showlegend=False
                        ))

        # Configuración de la visualización
        camera = dict(
            up=dict(x=0, y=1, z=0),
            center=dict(x=0, y=0, z=0),
            eye=dict(x=1.5, y=1.5, z=1.5)
        )

        fig.update_layout(
            scene=dict(
                aspectmode='data',
                camera=camera,
                xaxis=dict(showgrid=self.show_grid),
                yaxis=dict(showgrid=self.show_grid),
                zaxis=dict(showgrid=self.show_grid)
            ),
            showlegend=True,
            margin=dict(l=0, r=0, t=30, b=0),
            height=600
        )

        return fig

    def set_visualization_options(self, show_original: bool, show_deformed: bool, 
                                show_stress: bool, show_grid: bool, show_wireframe: bool):
        """
        Actualiza las opciones de visualización.
        """
        self.show_original = show_original
        self.show_deformed = show_deformed
        self.show_stress = show_stress
        self.show_grid = show_grid
        self.show_wireframe = show_wireframe

    def set_deformation_scale(self, scale: float):
        """
        Actualiza la escala de deformación.
        """
        self.deformation_scale = scale
