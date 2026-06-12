import streamlit as st
# =================================================================
# 🛑 BLINDAJE INTERNACIONAL INDESTRUCTIBLE (PRO-HAMBURGUESA)
# =================================================================
# Este código neutraliza al gato de GitHub y la barra de desarrollo
# basándose estrictamente en etiquetas de código inalterables por traducción.
st.markdown("""
<style>
/* 1. Liquidamos al gato al instante (Oculta todos los enlaces del header, el de la hamburguesa es un botón) */
header[data-testid="stHeader"] a {
    display: none !important;
}

/* 2. Ocultamos el contenedor de la derecha (Share, Star, Lápiz, 3 puntos) */
div[data-testid="stHeaderActionElements"] {
    display: none !important;
}

/* 3. Apagamos todos los botones intrusos de la derecha de la nube, 
      protegiendo CUALQUIER variante de la hamburguesa (Sidebar / Collapse) */
header[data-testid="stHeader"] button:not([data-testid*="idebar"]):not([data-testid*="ollapse"]) {
    display: none !important;
}
</style>
""", unsafe_allow_html=True)
# =================================================================
# 🚀 COORDENADA DE INYECCIÓN: EL NUEVO ESCUDO CORPORATIVO
# =================================================================
# Limpio, ordenado y con sus saltos de línea correspondientes

ruta_logo = "logo.png"

if os.path.exists(ruta_logo):
    # Dibuja el escudo premium adaptándose al ancho de la barra lateral
    st.sidebar.image(ruta_logo, use_container_width=True)
else:
    # Fallback por si acaso estás en local y no has movido el archivo
    st.sidebar.markdown("🎯 **GÉNESIS OMR**")

st.sidebar.caption("Plataforma de Evaluación Óptica v2.0")
st.sidebar.markdown("---")

# =================================================================
# 🏢 CONFIGURACIÓN ESTRUCTURAL DE LA PLATAFORMA ENTERPRISE
# =================================================================
st.set_page_config(
    page_title="Génesis Evaluaciones", 
    page_icon="🎯", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Importación de la estructura modular de la pirámide (Desde tu carpeta 'modulos')
try:
    from modulos import m0_gestion, m1_creador, m2_simulacro, m3_escaner, m4_dashboard
except ImportError as e:
    st.error(f"🚨 Falla de infraestructura de red: No se pudo cargar un módulo interno. Detalle: {e}")
    st.stop()

def main():
    # Estilización corporativa del menú lateral para aplastar a la competencia
    st.markdown("""
        <style>
        [data-testid="stSidebar"] { background-color: #0d1b2a; }
        [data-testid="stSidebar"] * { color: #ffffff; }
        div[data-testid="stSidebarNav"] { display: none; } /* Ocultar rutas por defecto */
        </style>
    """, unsafe_allow_html=True)

    with st.sidebar:
        # Tu logo de Flaticon corporativo original
        st.image("https://cdn-icons-png.flaticon.com/512/3285/3285816.png", width=100)
        st.markdown("## 🎯 GÉNESIS OMR")
        st.markdown("<p style='color: #d4af37; font-size:12px; margin-top:-10px;'>Plataforma de Evaluación Óptica v2.0</p>", unsafe_allow_html=True)
        st.markdown("---")
        
        # Panel de Comando Unificado
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

# ... (aquí termina tu enrutador con m4_dashboard.ejecutar()) ...

    
if __name__ == "__main__":
    main()
