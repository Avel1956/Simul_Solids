import numpy as np

class MohrCalculator:
    """
    Clase para realizar cálculos relacionados con el Círculo de Mohr.
    Permite calcular esfuerzos principales, esfuerzo cortante máximo,
    y transformación de esfuerzos para diferentes ángulos.
    """
    
    def __init__(self):
        """Inicializa el calculador del Círculo de Mohr."""
        pass
    
    def calculate_results(self, params):
        """
        Calcula los resultados basados en los parámetros de entrada.
        
        Args:
            params (dict): Diccionario con los parámetros de entrada:
                - sigma_x: Esfuerzo normal en dirección x
                - sigma_y: Esfuerzo normal en dirección y
                - tau_xy: Esfuerzo cortante en el plano xy
                - theta: Ángulo de rotación (opcional, para transformación)
                
        Returns:
            dict: Diccionario con los resultados calculados
        """
        # Extraer parámetros
        sigma_x = params.get('sigma_x', 0)
        sigma_y = params.get('sigma_y', 0)
        tau_xy = params.get('tau_xy', 0)
        theta = params.get('theta', 0)  # En grados
        
        # Convertir ángulo a radianes
        theta_rad = np.radians(theta)
        
        # Calcular esfuerzos principales
        sigma_avg = (sigma_x + sigma_y) / 2
        r = np.sqrt(((sigma_x - sigma_y) / 2) ** 2 + tau_xy ** 2)
        
        sigma_1 = sigma_avg + r
        sigma_2 = sigma_avg - r
        
        # Calcular ángulo principal (en grados)
        theta_p = np.degrees(np.arctan2(2 * tau_xy, sigma_x - sigma_y) / 2)
        
        # Asegurar que el ángulo principal esté entre -90 y 90 grados
        if theta_p < -90:
            theta_p += 180
        elif theta_p > 90:
            theta_p -= 180
        
        # Calcular esfuerzo cortante máximo
        tau_max = r
        
        # Calcular esfuerzos transformados para el ángulo theta
        sigma_x_prime = sigma_avg + ((sigma_x - sigma_y) / 2) * np.cos(2 * theta_rad) + tau_xy * np.sin(2 * theta_rad)
        sigma_y_prime = sigma_avg - ((sigma_x - sigma_y) / 2) * np.cos(2 * theta_rad) - tau_xy * np.sin(2 * theta_rad)
        tau_xy_prime = -((sigma_x - sigma_y) / 2) * np.sin(2 * theta_rad) + tau_xy * np.cos(2 * theta_rad)
        
        # Preparar resultados
        results = {
            'sigma_1': sigma_1,
            'sigma_2': sigma_2,
            'tau_max': tau_max,
            'theta_p': theta_p,
            'sigma_x_prime': sigma_x_prime,
            'sigma_y_prime': sigma_y_prime,
            'tau_xy_prime': tau_xy_prime,
            'center': sigma_avg,
            'radius': r
        }
        
        return results
    
    def calculate_circle_points(self, params, num_points=100):
        """
        Calcula los puntos para graficar el Círculo de Mohr.
        
        Args:
            params (dict): Diccionario con los parámetros de entrada
            num_points (int): Número de puntos para el círculo
            
        Returns:
            tuple: Arrays de valores sigma y tau para el círculo
        """
        results = self.calculate_results(params)
        
        # Extraer centro y radio del círculo
        center = results['center']
        radius = results['radius']
        
        # Generar puntos del círculo
        theta = np.linspace(0, 2 * np.pi, num_points)
        sigma = center + radius * np.cos(theta)
        tau = radius * np.sin(theta)
        
        return sigma, tau
    
    def calculate_transformed_element(self, params, angle):
        """
        Calcula el estado de esfuerzos para un elemento rotado.
        
        Args:
            params (dict): Diccionario con los parámetros de entrada
            angle (float): Ángulo de rotación en grados
            
        Returns:
            dict: Estado de esfuerzos transformado
        """
        # Copiar parámetros y actualizar ángulo
        new_params = params.copy()
        new_params['theta'] = angle
        
        # Calcular resultados para el ángulo dado
        results = self.calculate_results(new_params)
        
        return {
            'sigma_x': results['sigma_x_prime'],
            'sigma_y': results['sigma_y_prime'],
            'tau_xy': results['tau_xy_prime']
        }
