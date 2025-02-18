import numpy as np

class TorsionCalculator:
    def __init__(self):
        self.PI = np.pi

    def calculate_polar_moment_of_inertia(self, outer_diameter: float, inner_diameter: float) -> float:
        """
        Calcula el momento polar de inercia para una sección circular o tubular.
        
        Args:
            outer_diameter: Diámetro exterior en metros
            inner_diameter: Diámetro interior en metros
            
        Returns:
            Momento polar de inercia en m⁴
        """
        ro = outer_diameter / 2
        ri = inner_diameter / 2
        return (self.PI / 32) * (outer_diameter**4 - inner_diameter**4)

    def calculate_max_shear_stress(self, torque: float, outer_diameter: float, inner_diameter: float) -> float:
        """
        Calcula el esfuerzo cortante máximo.
        
        Args:
            torque: Momento torsor en N⋅m
            outer_diameter: Diámetro exterior en metros
            inner_diameter: Diámetro interior en metros
            
        Returns:
            Esfuerzo cortante máximo en Pa
        """
        J = self.calculate_polar_moment_of_inertia(outer_diameter, inner_diameter)
        r = outer_diameter / 2
        return (torque * r) / J

    def calculate_twist_angle(self, torque: float, length: float, shear_modulus: float, 
                            outer_diameter: float, inner_diameter: float) -> float:
        """
        Calcula el ángulo de torsión.
        
        Args:
            torque: Momento torsor en N⋅m
            length: Longitud en metros
            shear_modulus: Módulo de corte en GPa
            outer_diameter: Diámetro exterior en metros
            inner_diameter: Diámetro interior en metros
            
        Returns:
            Ángulo de torsión en radianes
        """
        J = self.calculate_polar_moment_of_inertia(outer_diameter, inner_diameter)
        # Convertir GPa a Pa
        G = shear_modulus * 1e9
        return (torque * length) / (G * J)

    def get_segment_rotation(self, angle: float, segment_index: int, total_segments: int) -> float:
        """
        Calcula la rotación para un segmento específico.
        
        Args:
            angle: Ángulo total de torsión en radianes
            segment_index: Índice del segmento
            total_segments: Número total de segmentos
            
        Returns:
            Ángulo de rotación para el segmento en radianes
        """
        return (angle * segment_index) / total_segments

    def calculate_results(self, params: dict) -> dict:
        """
        Calcula todos los resultados relevantes.
        
        Args:
            params: Diccionario con los parámetros:
                - length: Longitud en metros
                - outer_diameter: Diámetro exterior en metros
                - inner_diameter: Diámetro interior en metros
                - shear_modulus: Módulo de corte en GPa
                - torque: Momento torsor en N⋅m
                
        Returns:
            Diccionario con los resultados calculados
        """
        J = self.calculate_polar_moment_of_inertia(
            params['outer_diameter'], 
            params['inner_diameter']
        )
        
        twist_angle = self.calculate_twist_angle(
            params['torque'],
            params['length'],
            params['shear_modulus'],
            params['outer_diameter'],
            params['inner_diameter']
        )
        
        max_shear_stress = self.calculate_max_shear_stress(
            params['torque'],
            params['outer_diameter'],
            params['inner_diameter']
        )

        return {
            'polar_moment_of_inertia': J,
            'twist_angle': twist_angle,
            'twist_angle_degrees': np.degrees(twist_angle),
            'max_shear_stress': max_shear_stress
        }
