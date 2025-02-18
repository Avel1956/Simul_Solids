import streamlit as st
import os
import sys

# Añadir el directorio raíz al path para poder importar desde apps
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root_dir)

# Configurar la página antes de cualquier otra operación
st.set_page_config(
    page_title="Simulador de Torsión",
    page_icon="🌀",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Importar después de la configuración de la página
from apps.torsion.app import main

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        st.error(f"Error al cargar el simulador: {str(e)}")
        st.error("Por favor, intente recargar la página.")
