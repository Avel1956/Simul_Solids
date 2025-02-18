import numpy as np

class TraccionCalculator:
    def __init__(self):
        self.materiales = {
            'acero': {
                'nombre': 'Acero',
                'modulo_elasticidad': 210,  # GPa
                'limite_elastico': 250,     # MPa
                'resistencia_traccion': 400, # MPa
                'coef_poisson': 0.3
            },
            'aluminio': {
                'nombre': 'Aluminio',
                'modulo_elasticidad': 70,
                'limite_elastico': 95,
                'resistencia_traccion': 110,
                'coef_poisson': 0.33
            },
            'cobre': {
                'nombre': 'Cobre',
                'modulo_elasticidad': 120,
                'limite_elastico': 70,
                'resistencia_traccion': 220,
                'coef_poisson': 0.34
            }
        }
        self.current_strain = 0.0
        self.strain_rate = 0.001  # Tasa de deformación por paso
        self.max_strain = 0.2     # Deformación máxima

    def get_material_properties(self, material_name):
        """Obtiene las propiedades de un material."""
        return self.materiales.get(material_name)

    def calculate_stress_strain(self, material_name, strain):
        """Calcula el esfuerzo para una deformación dada."""
        material = self.materiales[material_name]
        E = material['modulo_elasticidad'] * 1000  # Convertir GPa a MPa
        yield_stress = material['limite_elastico']
        
        # Región elástica
        if strain <= yield_stress/E:
            stress = E * strain
        else:
            # Región plástica (modelo simplificado)
            elastic_strain = yield_stress/E
            plastic_strain = strain - elastic_strain
            # Endurecimiento por deformación simplificado
            hardening_factor = 0.1  # Factor de endurecimiento
            stress = yield_stress + hardening_factor * E * plastic_strain
            
            # Limitar al esfuerzo máximo
            stress = min(stress, material['resistencia_traccion'])
        
        return stress

    def get_next_strain(self):
        """Incrementa la deformación actual."""
        if self.current_strain < self.max_strain:
            self.current_strain += self.strain_rate
            return self.current_strain
        return None

    def reset_simulation(self):
        """Reinicia la simulación."""
        self.current_strain = 0.0
