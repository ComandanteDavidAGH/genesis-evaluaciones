import streamlit as st

st.set_page_config(page_title="Génesis Evaluaciones", page_icon="🎯", layout="wide")

# Importación de la artillería modular
from modulos import m1_creador, m2_simulacro, m4_dashboard

def main():
    st.markdown("""
        <style>
        [data-testid="stSidebar"] { background-color: #0d1b2a; }
        [data-testid="stSidebar"] * { color: #ffffff; }
        </style>
    """, unsafe_allow_html=True)

    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/3285/3285816.png", width=100)
        st.markdown("## 🎯 GÉNESIS OMR")
        st.markdown("---")
        
        menu = st.radio(
            "📍 SELECCIONE EL MÓDULO:",
            [
                "⚙️ 1. Creador de Pruebas",
                "📱 2. Despliegue Digital (Alumnos)",
                "👁️ 3. Escáner OMR (Cámara)",
                "📊 4. Dashboard Analítico"
            ]
        )
        st.markdown("---")
        st.caption("Fase de Desarrollo - Modo Estable")

    # Enrutador Maestro
    if menu == "⚙️ 1. Creador de Pruebas":
        m1_creador.ejecutar()
    elif menu == "📱 2. Despliegue Digital (Alumnos)":
        m2_simulacro.ejecutar() 
    elif menu == "👁️ 3. Escáner OMR (Cámara)":
        st.info("🚧 Módulo de Visión Artificial en construcción.")
    elif menu == "📊 4. Dashboard Analítico":
        m4_dashboard.ejecutar() # <--- ¡CONEXIÓN ESTABLECIDA!

if __name__ == "__main__":
    main()
