import numpy as np
import plotly.graph_objects as go

class TraccionVisualizer:
    def __init__(self):
        self.data = {}  # Almacena los datos de cada material
        self.colors = {
            'acero': '#1f77b4',    # azul
            'aluminio': '#ff7f0e',  # naranja
            'cobre': '#2ca02c'      # verde
        }

    def update_data(self, material_name, strain, stress):
        """Actualiza los datos de un material."""
        if material_name not in self.data:
            self.data[material_name] = {
                'strain': [0],
                'stress': [0]
            }
        
        self.data[material_name]['strain'].append(strain)
        self.data[material_name]['stress'].append(stress)

    def create_figure(self):
        """Crea la figura con las curvas esfuerzo-deformación."""
        fig = go.Figure()

        # Agregar curvas para cada material
        for material_name, data in self.data.items():
            fig.add_trace(
                go.Scatter(
                    x=data['strain'],
                    y=data['stress'],
                    mode='lines',
                    name=material_name.capitalize(),
                    line=dict(
                        color=self.colors.get(material_name, '#000000'),
                        width=2
                    )
                )
            )

        # Configuración de la gráfica
        fig.update_layout(
            title='Curvas Esfuerzo-Deformación',
            xaxis_title='Deformación (ε)',
            yaxis_title='Esfuerzo (σ) [MPa]',
            showlegend=True,
            height=600,
            hovermode='x unified'
        )

        # Configurar rangos de los ejes
        fig.update_xaxes(range=[0, 0.2])
        fig.update_yaxes(range=[0, 500])

        return fig

    def reset_data(self, material_name=None):
        """Reinicia los datos de un material o de todos."""
        if material_name:
            if material_name in self.data:
                del self.data[material_name]
        else:
            self.data = {}
