# Simulaciones de Ingeniería

Una plataforma web interactiva que ofrece diversas simulaciones de fenómenos de ingeniería mecánica, desarrollada con Streamlit.

## Simulaciones Disponibles

### 1. Simulador de Torsión
- Visualización 3D interactiva de deformación torsional
- Cálculo de esfuerzos y deformaciones
- Análisis paramétrico con diferentes geometrías y materiales
- Visualización de distribución de esfuerzos

### 2. Generador de Indeterminaciones
- Análisis de fuerzas en cables que soportan una barra rígida
- Cálculo de fuerzas y deformaciones en cada cable
- Visualización del sistema y su deformación
- Permite el uso de diferentes materiales y longitudes de cable

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
├── .streamlit/
│   └── config.toml
├── home.py
├── requirements.txt
└── README.md
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

Este proyecto está licenciado bajo la Licencia MIT - ver el archivo LICENSE para más detalles.
