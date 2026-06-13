import streamlit as st
import pandas as pd
from supabase import create_client, Client

# =================================================================
# 🔒 CONEXIÓN CON TOLERANCIA A FALLOS Y DIAGNÓSTICO EN VIVO
# =================================================================
def iniciar_conexion():
    # El código busca de forma inteligente cuál variable está activa
    if "REAL_SUPABASE_URL" in st.secrets:
        url = st.secrets["REAL_SUPABASE_URL"].strip()
        key = st.secrets["REAL_SUPABASE_KEY"].strip()
    elif "SUPABASE_URL" in st.secrets:
        url = st.secrets["SUPABASE_URL"].strip()
        key = st.secrets["SUPABASE_KEY"].strip()
    else:
        # Si no encuentra ninguna, no rompe la app; nos muestra la verdad en pantalla
        st.error("🔒 El servidor tiene la sección de Secrets completamente vacía o bloqueada.")
        st.info(f"📁 Nombres de variables que el servidor detecta actualmente: {list(st.secrets.keys())}")
        st.stop()
        
    return create_client(url, key)

def ejecutar():
    st.markdown("<h1 style='color: #0d1b2a;'>👥 Gestión de Estudiantes</h1>", unsafe_allow_html=True)
    st.caption("Control global de matrícula escolar sincronizado en vivo.")
    st.markdown("---")

    try:
        supabase = iniciar_conexion()
        resultado = supabase.table("data_estudiantes").select("ID_Estudiante, Nombre_Completo, Grado, Grupo, Correo_Institucional").execute()
        estudiantes_base = resultado.data
    except Exception as e:
        st.error(f"🚨 Error de enlace seguro: {e}")
        return

    if estudiantes_base:
        df_unicos = pd.DataFrame(estudiantes_base).drop_duplicates(subset=["ID_Estudiante"])
        st.metric("📊 Estudiantes Únicos Matriculados", len(df_unicos))
        st.dataframe(df_unicos[["ID_Estudiante", "Nombre_Completo", "Grado", "Grupo", "Correo_Institucional"]], use_container_width=True, hide_index=True)
    else:
        st.warning("⚠️ La tabla 'data_estudiantes' se conectó pero está vacía internamente.")
