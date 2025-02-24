# Simulaciones de Ingeniería

Una plataforma web interactiva que ofrece diversas simulaciones de fenómenos de ingeniería mecánica, desarrollada con Streamlit.

## Simulaciones Disponibles

### 1. Simulador de Torsión
- Visualización 3D interactiva de deformación torsional
- Cálculo de esfuerzos y deformaciones
- Análisis paramétrico con diferentes geometrías y materiales
- Visualización de distribución de esfuerzos

#### Teoría de Torsión
La torsión es la acción de torcer un objeto debido a un par de fuerzas aplicadas en direcciones opuestas. En elementos cilíndricos, la torsión genera esfuerzos cortantes que varían linealmente desde el eje neutro hasta la superficie exterior. La fórmula básica para el esfuerzo cortante debido a la torsión es:

\[ \tau = \frac{T \cdot r}{J} \]

donde:
- \( \tau \) es el esfuerzo cortante
- \( T \) es el momento torsor
- \( r \) es la distancia desde el eje neutro
- \( J \) es el momento polar de inercia

### 2. Generador de Indeterminaciones
- Análisis de fuerzas en cables que soportan una barra rígida
- Cálculo de fuerzas y deformaciones en cada cable
- Visualización del sistema y su deformación
- Permite el uso de diferentes materiales y longitudes de cable

#### Teoría de Indeterminaciones
En sistemas estructurales, una indeterminación estática ocurre cuando hay más incógnitas que ecuaciones de equilibrio disponibles. Para resolver estos sistemas, se utilizan métodos adicionales como la compatibilidad de deformaciones y las propiedades de los materiales.

### 3. Simulador de Tracción
- Analiza los esfuerzos y deformaciones en elementos sometidos a tracción
- Visualiza la curva esfuerzo-deformación
- Calcula parámetros clave

#### Teoría de Tracción
La tracción es la acción de estirar un objeto aplicando fuerzas en direcciones opuestas. El esfuerzo normal debido a la tracción se calcula como:

\[ \sigma = \frac{F}{A} \]

donde:
- \( \sigma \) es el esfuerzo normal
- \( F \) es la fuerza aplicada
- \( A \) es el área de la sección transversal

### 4. Simulador de Flexión
- Analiza los esfuerzos y deformaciones en elementos sometidos a flexión pura
- Visualiza la distribución de esfuerzos

#### Teoría de Flexión
La flexión ocurre cuando un momento flector se aplica a una viga, causando que se doble. El esfuerzo normal debido a la flexión se calcula como:

\[ \sigma = \frac{M \cdot y}{I} \]

donde:
- \( \sigma \) es el esfuerzo normal
- \( M \) es el momento flector
- \( y \) es la distancia desde el eje neutro
- \( I \) es el momento de inercia de área

## Requisitos

- Python 3.8 o superior
- pip (gestor de paquetes de Python)

## Instalación

1. Clonar el repositorio:
```bash
git clone [url-del-repositorio]
cd [nombre-del-directorio]
```

2. Instalar las dependencias:
```bash
pip install -r requirements.txt
```

## Uso

1. Ejecutar la aplicación:
```bash
streamlit run home.py
```

2. Abrir el navegador web en:
```
http://localhost:8501
```

## Estructura del Proyecto

```
.
├── apps/
│   ├── torsion/
│   │   ├── app.py
│   │   ├── torsion_calculator.py
│   │   └── torsion_visualizer.py
│   │   └── __init__.py
│   ├── indeterminacion/
│   │   ├── app.py
│   │   ├── indeterminacion_calculator.py
│   │   └── indeterminacion_visualizer.py
│   │   └── __init__.py
│   └── __init__.py
├── pages/
│   └── 1_Simulador_de_Torsion.py
│   └── 2_Simulador_de_Traccion.py
│   └── 3_Generador_de_Indeterminaciones.py
│   └── 4_Simulador_de_Flexion.py
├── .streamlit/
│   └── config.toml
├── home.py
├── requirements.txt
├── assets/
│   ├── flexion.png
│   ├── indeterminacion.png
│   ├── torsion.png
│   └── traccion.png
├── README.md
└── styles.css
```

## Características

- Interfaz de usuario intuitiva y responsive
- Visualizaciones 3D interactivas
- Cálculos en tiempo real
- Documentación integrada con ecuaciones y teoría
- Diseño modular para fácil extensión

## Próximas Funcionalidades

- Más simulaciones de fenómenos mecánicos
- Exportación de resultados
- Comparación de diferentes casos
- Biblioteca de materiales predefinidos

## Contribuir

Si deseas contribuir al proyecto:

1. Haz un Fork del repositorio
2. Crea una rama para tu funcionalidad (`git checkout -b feature/nueva-funcionalidad`)
3. Haz commit de tus cambios (`git commit -am 'Añadir nueva funcionalidad'`)
4. Haz push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crea un Pull Request

## Licencia

Este proyecto está licenciado bajo los términos de la licencia MIT.