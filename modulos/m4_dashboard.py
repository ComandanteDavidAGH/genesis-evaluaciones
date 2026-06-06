import streamlit as st
import pandas as pd
from supabase import create_client, Client

# =================================================================
# 🔌 CONEXIÓN AL BÚNKER (VERSIÓN BLINDADA)
# =================================================================
@st.cache_resource
def iniciar_conexion():
    url = st.secrets["SUPABASE_URL"].replace('"', '').replace("'", "").strip()
    key = st.secrets["SUPABASE_KEY"].replace('"', '').replace("'", "").strip()
    return create_client(url, key)

def ejecutar():
    st.markdown("""
    <style>
    .titulo-dashboard { color: #0d1b2a; border-bottom: 3px solid #d4af37; padding-bottom: 5px; font-family: 'Arial Black'; }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("<h1 class='titulo-dashboard'>📊 Centro de Inteligencia: Dashboard Analítico</h1>", unsafe_allow_html=True)
    st.caption("Panel de control gerencial para el análisis del rendimiento académico de las tropas.")

    try:
        supabase: Client = iniciar_conexion()
    except Exception:
        st.error("⚠️ Falla de conexión con el centro de datos.")
        return

    # 1. Extraer los datos de las calificaciones de Supabase
    with st.spinner("Extrayendo métricas desde el búnker..."):
        try:
            respuesta = supabase.table("respuestas_estudiantes").select("*").execute()
            datos = respuesta.data
        except Exception as e:
            st.error(f"💥 Error al conectar con las tablas: {e}")
            return

    if not datos:
        st.info("📭 Aún no hay registros de estudiantes evaluados para generar estadísticas.")
        return

    # 2. Procesamiento de Datos con Pandas
    df = pd.DataFrame(datos)
    
    # Convertir fecha a formato legible
    df['fecha_formateada'] = pd.to_datetime(df['created_at']).dt.strftime('%Y-%m-%d %H:%M')

    # 3. Bloque de Métricas de Alto Nivel (HUD)
    total_evaluados = len(df)
    promedio_general = df['porcentaje'].mean()
    aprobados = len(df[df['porcentaje'] >= 60.0])
    tasa_aprobacion = (aprobados / total_evaluados) * 100 if total_evaluados > 0 else 0

    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    
    with c1:
        st.metric(label="👥 Total Alumnos Evaluados", value=f"{total_evaluados} Soldados")
    with c2:
        st.metric(label="📈 Promedio de Efectividad General", value=f"{promedio_general:.1f}%")
    with c3:
        st.metric(label="🎯 Tasa de Aprobación", value=f"{tasa_aprobacion:.1f}%", delta=f"{aprobados} Alumnos pasaron")

    st.markdown("---")

    # 4. Tabla de Rendimiento Detallada
    st.markdown("### 📋 Bitácora de Calificaciones Históricas")
    
    df_visual = df[[
        'estudiante', 'nombre_prueba', 'puntaje_obtenido', 
        'puntaje_maximo', 'porcentaje', 'fecha_formateada'
    ]].copy()
    
    df_visual.columns = ['Estudiante', 'Simulacro', 'Puntaje', 'Máximo Posible', '% Efectividad', 'Fecha de Entrega']
    
    st.dataframe(
        df_visual.sort_values(by="Fecha de Entrega", ascending=False),
        use_container_width=True,
        hide_index=True
    )

if __name__ == "__main__":
    ejecutar()
