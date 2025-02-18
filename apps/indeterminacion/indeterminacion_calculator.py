"""
This module provides the calculator class for analyzing forces in cables supporting a rigid bar.
It handles all physics calculations and step-by-step solution generation.
"""

import numpy as np
from dataclasses import dataclass
from typing import Dict, Tuple, List

@dataclass
class MaterialProperties:
    """Predefined material properties."""
    STEEL = 200e9  # 200 GPa
    ALUMINUM = 70e9  # 70 GPa
    TITANIUM = 110e9  # 110 GPa

@dataclass
class CableParameters:
    """Parameters for a single cable."""
    E: float  # Young's modulus (Pa)
    A: float  # Cross-sectional area (m²)
    L: float  # Length (m)

    @property
    def stiffness(self) -> float:
        """Calculate the cable's stiffness k = EA/L."""
        return (self.E * self.A) / self.L

class IndeterminacionCalculator:
    """Calculator for analyzing forces in a two-cable system."""
    
    def __init__(self):
        """Initialize the calculator with default material properties."""
        self.materials = {
            "Acero": MaterialProperties.STEEL,
            "Aluminio": MaterialProperties.ALUMINUM,
            "Titanio": MaterialProperties.TITANIUM
        }

    def calculate_forces(self, cable1: CableParameters, cable2: CableParameters, 
                        load: float) -> Dict[str, float]:
        """
        Calculate forces and deformations in the two-cable system.
        
        Args:
            cable1: Parameters for the first cable
            cable2: Parameters for the second cable
            load: Applied load (N)
            
        Returns:
            Dictionary containing calculated values (forces, deformations, etc.)
        """
        # Calculate stiffness for each cable
        k1 = cable1.stiffness
        k2 = cable2.stiffness
        
        # Calculate forces using stiffness ratio
        F1 = (load * k1) / (k1 + k2)
        F2 = load - F1
        
        # Calculate deformations
        delta1 = F1 * cable1.L / (cable1.E * cable1.A)
        delta2 = F2 * cable2.L / (cable2.E * cable2.A)
        
        return {
            "k1": k1,
            "k2": k2,
            "F1": F1,
            "F2": F2,
            "delta1": delta1,
            "delta2": delta2,
            "F1_percentage": (F1/load) * 100,
            "F2_percentage": (F2/load) * 100
        }

    def generate_random_example(self) -> Tuple[CableParameters, CableParameters, float]:
        """
        Generate random but realistic parameters for both cables.
        
        Returns:
            Tuple containing parameters for both cables and the load
        """
        # Generate realistic random values
        A1 = np.random.uniform(50, 150) * 1e-6  # 50-150 mm² converted to m²
        A2 = np.random.uniform(50, 150) * 1e-6
        L1 = np.random.uniform(1, 3)  # 1-3 m
        L2 = np.random.uniform(1, 3)
        load = np.random.uniform(5000, 15000)  # 5-15 kN
        
        # Randomly select materials
        materials = list(self.materials.values())
        E1 = np.random.choice(materials)
        E2 = np.random.choice(materials)
        
        return (
            CableParameters(E1, A1, L1),
            CableParameters(E2, A2, L2),
            load
        )

    def generate_solution_steps(self, cable1: CableParameters, cable2: CableParameters,
                              load: float, results: Dict[str, float]) -> List[Dict[str, str]]:
        """
        Generate step-by-step solution explanation with LaTeX equations.
        
        Args:
            cable1: Parameters for first cable
            cable2: Parameters for second cable
            load: Applied load
            results: Dictionary of calculated results
            
        Returns:
            List of dictionaries containing step titles and LaTeX equations
        """
        steps = []
        
        # Step 1: Define stiffnesses
        steps.append({
            "title": "Paso 1: Definición de Rigideces",
            "content": "La rigidez de cada cable se calcula como k = EA/L:",
            "equation": f"""
                k_1 = \\frac{{E_1A_1}}{{L_1}} = \\frac{{{cable1.E/1e9:.0f} \\cdot 10^9 \\cdot {cable1.A*1e6:.2f}}}{{{cable1.L}}} = {results['k1']:.2e} \\text{{ N/m}}
                
                k_2 = \\frac{{E_2A_2}}{{L_2}} = \\frac{{{cable2.E/1e9:.0f} \\cdot 10^9 \\cdot {cable2.A*1e6:.2f}}}{{{cable2.L}}} = {results['k2']:.2e} \\text{{ N/m}}
            """
        })
        
        # Step 2: Compatibility equation
        steps.append({
            "title": "Paso 2: Ecuación de Compatibilidad",
            "content": "El desplazamiento vertical es igual para ambos cables:",
            "equation": "\\frac{F_1}{k_1} = \\frac{F_2}{k_2}"
        })
        
        # Step 3: Force equilibrium
        steps.append({
            "title": "Paso 3: Equilibrio de Fuerzas",
            "content": "La suma de fuerzas debe igualar la carga aplicada:",
            "equation": f"F_1 + F_2 = P = {load:.2f} \\text{{ N}}"
        })
        
        # Step 4: System solution
        steps.append({
            "title": "Paso 4: Solución del Sistema",
            "content": "Combinando las ecuaciones anteriores:",
            "equation": f"""
                F_1 = \\frac{{P \\cdot k_1}}{{k_1 + k_2}} = \\frac{{{load:.2f} \\cdot {results['k1']:.2e}}}{{{results['k1']:.2e} + {results['k2']:.2e}}} = {results['F1']:.2f} \\text{{ N}}
                
                F_2 = \\frac{{P \\cdot k_2}}{{k_1 + k_2}} = \\frac{{{load:.2f} \\cdot {results['k2']:.2e}}}{{{results['k1']:.2e} + {results['k2']:.2e}}} = {results['F2']:.2f} \\text{{ N}}
            """
        })
        
        # Step 5: Deformations
        steps.append({
            "title": "Paso 5: Cálculo de Deformaciones",
            "content": "Las deformaciones en cada cable son:",
            "equation": f"""
                \\Delta L_1 = \\frac{{F_1L_1}}{{E_1A_1}} = \\frac{{{results['F1']:.2f} \\cdot {cable1.L}}}{{{cable1.E/1e9:.0f} \\cdot 10^9 \\cdot {cable1.A*1e6:.2f}}} = {results['delta1']*1000:.2f} \\text{{ mm}}
                
                \\Delta L_2 = \\frac{{F_2L_2}}{{E_2A_2}} = \\frac{{{results['F2']:.2f} \\cdot {cable2.L}}}{{{cable2.E/1e9:.0f} \\cdot 10^9 \\cdot {cable2.A*1e6:.2f}}} = {results['delta2']*1000:.2f} \\text{{ mm}}
            """
        })
        
        return steps
