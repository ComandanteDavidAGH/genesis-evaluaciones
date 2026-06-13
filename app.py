import streamlit as st
import os

from modulos import m0_gestion, m1_creador, m2_simulacro, m3_escaner, m4_dashboard

st.set_page_config(
    page_title="Génesis Evaluaciones", 
    page_icon="🎯", 
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
header[data-testid="stHeader"] a {
    display: none !important;
}
div[data-testid="stHeaderActionElements"] {
    display: none !important;
}
header[data-testid="stHeader"] button:not([data-testid*="idebar"]):not([data-testid*="ollapse"]) {
    display: none !important;
}
</style>
""", unsafe_allow_html=True)

def main():
    st.markdown("""
        <style>
        [data-testid="stSidebar"] { background-color: #0d1b2a; }
        [data-testid="stSidebar"] * { color: #ffffff; }
        div[data-testid="stSidebarNav"] { display: none; } 
        </style>
    """, unsafe_allow_html=True)

    with st.sidebar:
        ruta_logo = "logo.png"
        if os.path.exists(ruta_logo):
            st.image(ruta_logo, use_container_width=True)
        else:
            st.markdown("## 🎯 GÉNESIS OMR")
            
        st.markdown("<p style='color: #d4af37; font-size:12px; margin-top:-10px;'>Plataforma de Evaluación Óptica v2.0</p>", unsafe_allow_html=True)
        st.markdown("---")
        
        menu = st.sidebar.radio(
            "📍 SELECCIONE EL MÓDULO:",
            [
                "👥 0. Gestión de Estudiantes",
                "⚙️ 1. Creador de Pruebas",
                "📱 2. Despliegue Digital (Alumnos)",
                "👁️ 3. Escáner OMR (Cámara)",
                "📊 4. Dashboard Analítico"
            ]
        )
        st.markdown("---")
        st.caption("Fase de Desarrollo - Modo Estable")

    if menu == "👥 0. Gestión de Estudiantes":
        m0_gestion.ejecutar()
    elif menu == "⚙️ 1. Creador de Pruebas":
        m1_creador.ejecutar()
    elif menu == "📱 2. Despliegue Digital (Alumnos)":
        m2_simulacro.ejecutar() 
    elif menu == "👁️ 3. Escáner OMR (Cámara)":
        m3_escaner.ejecutar()
    elif menu == "📊 4. Dashboard Analítico":
        m4_dashboard.ejecutar()

if __name__ == "__main__":
    main()
