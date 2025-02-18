"""
This module provides visualization functionality for the two-cable system.
It creates matplotlib figures showing the initial and deformed states of the system.
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Arrow
from typing import Dict, Tuple

class IndeterminacionVisualizer:
    """Visualizer for the two-cable system using matplotlib."""
    
    def __init__(self):
        """Initialize the visualizer with default style settings."""
        self.style = {
            'initial': {
                'color': '#bdc3c7',
                'linestyle': '--',
                'linewidth': 1
            },
            'deformed': {
                'color': '#2ecc71',
                'linestyle': '-',
                'linewidth': 2
            },
            'text_color': '#333333',
            'arrow_color': '#2ecc71'
        }

    def create_figure(self, L1: float, L2: float, load: float, 
                     results: Dict[str, float] = None) -> plt.Figure:
        """
        Create a matplotlib figure showing the system configuration.
        
        Args:
            L1: Length of cable 1 (m)
            L2: Length of cable 2 (m)
            load: Applied load (N)
            results: Optional dictionary with calculation results for showing deformed state
            
        Returns:
            Matplotlib figure object
        """
        # Create figure and axis
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Set up the coordinate system
        max_length = max(L1, L2)
        margin = max_length * 0.2
        ax.set_xlim(-max_length - margin, max_length + margin)
        ax.set_ylim(-max_length * 0.2, max_length + margin)
        
        # Calculate key points
        bar_width = max_length
        bar_height = max_length * 0.05
        
        # Base points for the bar
        bar_left = -bar_width/2
        bar_right = bar_width/2
        bar_y = 0
        
        # Top anchor points (with some horizontal offset for visual clarity)
        top_left_x = bar_left - (L1 * 0.3)
        top_right_x = bar_right + (L2 * 0.3)
        top_y = max_length
        
        # Draw initial configuration
        self._draw_configuration(ax, 
                               (top_left_x, top_y), (bar_left, bar_y),
                               (top_right_x, top_y), (bar_right, bar_y),
                               bar_width, bar_height,
                               self.style['initial'])
        
        # Add labels for initial configuration
        self._add_labels(ax, L1, L2, load, 
                        (top_left_x, top_y), (top_right_x, top_y),
                        (bar_left, bar_y), (bar_right, bar_y))
        
        # Draw deformed configuration if results are provided
        if results:
            # Calculate deformed positions
            deformed_y = -results['delta1']  # Use the smaller deformation
            
            self._draw_configuration(ax,
                                   (top_left_x, top_y), (bar_left, deformed_y),
                                   (top_right_x, top_y), (bar_right, deformed_y),
                                   bar_width, bar_height,
                                   self.style['deformed'])
            
            # Add load arrow
            arrow_length = min(max_length * 0.2, load/1000)
            ax.add_patch(Arrow(0, deformed_y - bar_height/2, 0, -arrow_length,
                             width=arrow_length*0.3, color=self.style['arrow_color']))
        
        # Final adjustments
        ax.set_aspect('equal')
        ax.axis('off')
        plt.tight_layout()
        
        return fig

    def _draw_configuration(self, ax: plt.Axes, 
                          top_left: Tuple[float, float], bottom_left: Tuple[float, float],
                          top_right: Tuple[float, float], bottom_right: Tuple[float, float],
                          bar_width: float, bar_height: float,
                          style: Dict[str, str]):
        """Draw a complete configuration (either initial or deformed)."""
        # Draw cables
        ax.plot([top_left[0], bottom_left[0]], [top_left[1], bottom_left[1]],
                color=style['color'], linestyle=style['linestyle'], 
                linewidth=style['linewidth'])
        ax.plot([top_right[0], bottom_right[0]], [top_right[1], bottom_right[1]],
                color=style['color'], linestyle=style['linestyle'],
                linewidth=style['linewidth'])
        
        # Draw bar
        bar = Rectangle((bottom_left[0], bottom_left[1] - bar_height/2),
                       bar_width, bar_height,
                       fill=False,
                       color=style['color'],
                       linestyle=style['linestyle'],
                       linewidth=style['linewidth'])
        ax.add_patch(bar)
        
        # Add anchor points
        for point in [top_left, top_right, bottom_left, bottom_right]:
            ax.plot(point[0], point[1], 'o',
                   color=style['color'],
                   markersize=6)

    def _add_labels(self, ax: plt.Axes,
                   L1: float, L2: float, load: float,
                   top_left: Tuple[float, float], top_right: Tuple[float, float],
                   bottom_left: Tuple[float, float], bottom_right: Tuple[float, float]):
        """Add labels to the diagram."""
        # Cable labels
        ax.text(top_left[0], top_left[1] + 0.1, 'Cable 1',
                ha='center', va='bottom', color=self.style['text_color'])
        ax.text(top_right[0], top_right[1] + 0.1, 'Cable 2',
                ha='center', va='bottom', color=self.style['text_color'])
        
        # Length labels
        ax.text((top_left[0] + bottom_left[0])/2 - 0.2, (top_left[1] + bottom_left[1])/2,
                f'L₁ = {L1:.2f} m', ha='right', va='center',
                color=self.style['text_color'])
        ax.text((top_right[0] + bottom_right[0])/2 + 0.2, (top_right[1] + bottom_right[1])/2,
                f'L₂ = {L2:.2f} m', ha='left', va='center',
                color=self.style['text_color'])
        
        # Load label
        ax.text(0, -0.3, f'P = {load:.0f} N',
                ha='center', va='top', color=self.style['text_color'])
