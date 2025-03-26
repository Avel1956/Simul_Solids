# Simulaciones de Ingeniería Mecánica

Una plataforma web interactiva que ofrece simulaciones avanzadas de fenómenos fundamentales en ingeniería mecánica, desarrollada con Streamlit. Esta herramienta sirve tanto como simulador práctico como recurso educativo para el estudio de la mecánica de materiales.

## Fundamentos Teóricos y Simulaciones Disponibles

### 1. Simulador de Torsión

#### Teoría Fundamental
La torsión es un fenómeno mecánico donde un momento torsor produce una deformación angular en un elemento. Los principios fundamentales incluyen:

- **Ley de Hooke para Torsión**: 
  
  $$\gamma = \frac{\tau}{G}$$
  
  donde $\gamma$ es la deformación angular, $\tau$ es el esfuerzo cortante, y $G$ es el módulo de cortante

- **Distribución de Esfuerzos**: 
  
  $$\tau = \frac{T \cdot r}{J}$$
  
  - $T$: Momento torsor
  - $r$: Distancia al eje neutro
  - $J$: Momento polar de inercia
  - Para sección circular: $$J = \frac{\pi d^4}{32}$$

- **Ángulo de Torsión**: 
  
  $$\theta = \frac{TL}{JG}$$
  
  donde $L$ es la longitud del elemento

#### Aplicaciones Prácticas
- Diseño de ejes de transmisión
- Análisis de elementos mecánicos rotativos
- Dimensionamiento de elementos de máquinas

### 2. Simulador de Tracción

#### Teoría Fundamental
La tracción estudia el comportamiento de materiales bajo cargas axiales. Conceptos clave:

- **Ley de Hooke**: 
  
  $$\sigma = E\varepsilon$$
  
  - $\sigma$: Esfuerzo normal
  - $E$: Módulo de elasticidad
  - $\varepsilon$: Deformación unitaria

- **Deformación Unitaria**: 
  
  $$\varepsilon = \frac{\Delta L}{L_0}$$
  
  donde $\Delta L$ es el cambio en longitud y $L_0$ es la longitud inicial

- **Diagrama Esfuerzo-Deformación**:
  - Región elástica
  - Punto de fluencia
  - Región plástica
  - Resistencia última
  - Fractura

#### Propiedades Mecánicas Calculadas
- Módulo de elasticidad (E)
- Resistencia a la fluencia (Sy)
- Resistencia última (Su)
- Ductilidad
- Tenacidad

### 3. Simulador de Flexión

#### Teoría Fundamental
La flexión ocurre cuando se aplican momentos que causan curvatura en el elemento. Principios básicos:

- **Ecuación de la Flexión**: 
  
  $$\sigma = \frac{My}{I}$$
  
  - $M$: Momento flector
  - $y$: Distancia al eje neutro
  - $I$: Momento de inercia

- **Deformación por Flexión**: 
  
  $$\varepsilon = \frac{y}{\rho}$$
  
  donde $\rho$ es el radio de curvatura

- **Momento de Inercia**:
  - Rectangular: $$I = \frac{bh^3}{12}$$
  - Circular: $$I = \frac{\pi d^4}{64}$$

#### Aplicaciones
- Diseño de vigas
- Análisis estructural
- Cálculo de deflexiones

### 4. Generador de Indeterminaciones

#### Teoría Fundamental
Los sistemas estáticamente indeterminados requieren análisis adicional más allá de las ecuaciones de equilibrio:

- **Ecuaciones de Compatibilidad**
- **Método de Superposición**
- **Teorema de Castigliano**

#### Principios de Análisis
1. Identificación del grado de indeterminación
2. Ecuaciones de equilibrio
3. Ecuaciones de compatibilidad
4. Solución del sistema de ecuaciones

### 5. Simulador del Círculo de Mohr

#### Teoría Fundamental
El Círculo de Mohr es una representación gráfica del estado de esfuerzos en un punto que permite visualizar la transformación de esfuerzos. Los conceptos clave incluyen:

- **Transformación de Esfuerzos**:
  
  $$\sigma_x' = \frac{\sigma_x + \sigma_y}{2} + \frac{\sigma_x - \sigma_y}{2}\cos(2\theta) + \tau_{xy}\sin(2\theta)$$
  
  $$\tau_{xy}' = -\frac{\sigma_x - \sigma_y}{2}\sin(2\theta) + \tau_{xy}\cos(2\theta)$$

- **Esfuerzos Principales**:
  
  $$\sigma_{1,2} = \frac{\sigma_x + \sigma_y}{2} \pm \sqrt{\left(\frac{\sigma_x - \sigma_y}{2}\right)^2 + \tau_{xy}^2}$$

- **Esfuerzo Cortante Máximo**:
  
  $$\tau_{max} = \sqrt{\left(\frac{\sigma_x - \sigma_y}{2}\right)^2 + \tau_{xy}^2}$$

- **Ángulo Principal**:
  
  $$\theta_p = \frac{1}{2}\tan^{-1}\left(\frac{2\tau_{xy}}{\sigma_x - \sigma_y}\right)$$

#### Características del Simulador
- Visualización interactiva del Círculo de Mohr
- Cálculo de esfuerzos principales y cortante máximo
- Transformación de esfuerzos para cualquier ángulo
- Representación gráfica de estados de esfuerzo

#### Aplicaciones
- Análisis de falla en materiales
- Diseño de elementos estructurales
- Análisis de concentración de esfuerzos
- Determinación de planos críticos
- Estudio de estados de esfuerzo complejos

## Instalación y Configuración

### Requisitos del Sistema
- Python 3.8+
- Bibliotecas principales:
  - Streamlit
  - NumPy
  - Matplotlib
  - Three.js (para visualizaciones 3D)

### Proceso de Instalación

1. Clonar el repositorio:
```bash
git clone [url-del-repositorio]
cd [nombre-del-directorio]
```

2. Crear y activar entorno virtual (recomendado):
```bash
python -m venv venv
# En Windows:
venv\Scripts\activate
# En Unix/MacOS:
source venv/bin/activate
```

3. Instalar dependencias:
```bash
pip install -r requirements.txt
```

## Guía de Uso

### Iniciar la Aplicación
```bash
streamlit run home.py
```

### Ejemplos Prácticos

#### Análisis de Torsión
1. Seleccionar geometría del elemento
2. Ingresar propiedades del material
3. Aplicar momento torsor
4. Analizar distribución de esfuerzos

#### Ensayo de Tracción
1. Seleccionar material
2. Definir dimensiones de la probeta
3. Aplicar carga
4. Analizar curva esfuerzo-deformación

## Arquitectura del Software

### Estructura Modular
```
apps/
├── módulo/
│   ├── calculator.py    # Lógica de cálculo
│   ├── visualizer.py    # Visualización
│   └── app.py          # Interfaz de usuario
```



## Contribuciones y Desarrollo

### Guías de Contribución
1. Fork del repositorio
2. Crear rama de feature
3. Implementar cambios
4. Documentar código
5. Crear Pull Request

### Estándares de Código
- PEP 8 para Python
- Documentación con docstrings
- Tests unitarios requeridos

## Licencia
Este proyecto está bajo la Licencia MIT. Ver el archivo LICENSE para más detalles.
