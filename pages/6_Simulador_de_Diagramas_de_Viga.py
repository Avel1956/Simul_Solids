import streamlit as st
from apps.beam_diagrams.app import main

# Set page config
st.set_page_config(layout="wide", page_title="Beam Diagram Generator")

if __name__ == "__main__":
    main()
