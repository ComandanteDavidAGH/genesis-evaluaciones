import streamlit as st

# Configuración global de la página (Debe ser la primera línea de Streamlit)
st.set_page_config(page_title="Génesis Evaluaciones", page_icon="🎯", layout="wide")

# Importación de los módulos tácticos
from modulos import m1_creador

def main():
    # Estilos del menú lateral
    st.markdown("""
        <style>
        [data-testid="stSidebar"] { background-color: #0d1b2a; }
        [data-testid="stSidebar"] * { color: #ffffff; }
        </style>
    """, unsafe_allow_html=True)

    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/3285/3285816.png", width=100) # Ícono temporal
        st.markdown("## 🎯 GÉNESIS OMR")
        st.markdown("---")
        
        # Sistema de Navegación
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
        st.caption("Fase de Desarrollo - Modo Aislado")

    # Enrutador Maestro
    if menu == "⚙️ 1. Creador de Pruebas":
        m1_creador.ejecutar()
    elif menu == "📱 2. Despliegue Digital (Alumnos)":
        st.info("🚧 Módulo de respuesta digital en construcción. Aquí los alumnos verán el simulacro.")
    elif menu == "👁️ 3. Escáner OMR (Cámara)":
        st.info("🚧 Módulo de Visión Artificial en construcción. Aquí conectaremos la cámara.")
    elif menu == "📊 4. Dashboard Analítico":
        st.info("🚧 Centro de Inteligencia en construcción. Aquí veremos la campana de Gauss.")

if __name__ == "__main__":
    main()
