import streamlit as st
import os

# =================================================================
# 🏢 1. CONFIGURACIÓN ESTRUCTURAL (DEBE SER LA PRIMERA LÍNEA DE ST)
# =================================================================
st.set_page_config(
    page_title="Génesis Evaluaciones", 
    page_icon="🎯", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# =================================================================
# 🛑 2. PROTOCOLO DE BLINDAJE INTERNACIONAL INDESTRUCTIBLE
# =================================================================
st.markdown("""
<style>
/* Liquidamos al gato al instante de la barra superior */
header[data-testid="stHeader"] a {
    display: none !important;
}
/* Ocultamos el contenedor de desarrollo de la derecha */
div[data-testid="stHeaderActionElements"] {
    display: none !important;
}
/* Apagamos botones intrusos protegiendo la hamburguesa */
header[data-testid="stHeader"] button:not([data-testid*="idebar"]):not([data-testid*="ollapse"]) {
    display: none !important;
}
</style>
""", unsafe_allow_html=True)

# =================================================================
# 📦 3. INFRAESTRUCTURA DE RED Y MÓDULOS (AL BORDE IZQUIERDO)
# =================================================================
from modulos import m0_gestion, m1_creador, m2_simulacro, m3_escaner, m4_dashboard

# =================================================================
# 🖥️ 4. EJECUCIÓN DEL ENTORNO PRINCIPAL
# =================================================================
def main():
    # Estilización corporativa del menú lateral
    st.markdown("""
        <style>
        [data-testid="stSidebar"] { background-color: #0d1b2a; }
        [data-testid="stSidebar"] * { color: #ffffff; }
        div[data-testid="stSidebarNav"] { display: none; } 
        </style>
    """, unsafe_allow_html=True)

    with st.sidebar:
        # -------------------------------------------------------------
        # INTERSECCIÓN DEL ESCUDO PREMIUM (REEMPLAZO DEL RODILLO VIEJO)
        # -------------------------------------------------------------
        ruta_logo = "logo.png"
        
        if os.path.exists(ruta_logo):
            # Tu nuevo escudo corporativo en español toma el control absoluto
            st.image(ruta_logo, use_container_width=True)
        else:
            # Resguardo de texto premium si el archivo no ha cargado
            st.markdown("## 🎯 GÉNESIS OMR")
            
        st.markdown("<p style='color: #d4af37; font-size:12px; margin-top:-10px;'>Plataforma de Evaluación Óptica v2.0</p>", unsafe_allow_html=True)
        st.markdown("---")
        
        # Panel de Comando Unificado (Se mantienen tus componentes intactos)
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

    # =================================================================
    # 🚀 ENRUTADOR MAESTRO DE TRÁFICO MULTI-MÓDULO
    # =================================================================
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
