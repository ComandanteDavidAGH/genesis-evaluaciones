import streamlit as st
import pandas as pd
from supabase import create_client, Client


def iniciar_conexion():
    url = st.secrets["SUPABASE_URL"].replace('"', '').replace("'", "").strip()
    key = st.secrets["SUPABASE_KEY"].replace('"', '').replace("'", "").strip()
    return create_client(url, key)

def ejecutar():
    st.markdown("<h1 style='color: #0d1b2a;'>👥 Gestión de Estudiantes Institutional</h1>", unsafe_allow_html=True)
    st.caption("Control global de matrícula escolar sincronizado con la base central.")
    st.markdown("---")

    try:
        supabase = iniciar_conexion()
        # Extracción directa de tu tabla unificada sin datos espejo
        resultado = supabase.table("data_estudiantes").select("ID_Estudiante, Nombre_Completo, Grado, Grupo, Correo_Institucional").execute()
        estudiantes_base = resultado.data
    except Exception as e:
        st.error(f"🚨 Error de enlace con 'data_estudiantes': {e}")
        return

    if estudiantes_base:
        # Filtro de microsegundos para limpiar las filas duplicadas de las materias
        df_unicos = pd.DataFrame(estudiantes_base).drop_duplicates(subset=["ID_Estudiante"])
        
        # Panel Métrico
        st.metric("📊 Estudiantes Únicos Matriculados", len(df_unicos))
        
        # Despliegue de la Tabla Real
        st.dataframe(
            df_unicos[["ID_Estudiante", "Nombre_Completo", "Grado", "Grupo", "Correo_Institucional"]],
            use_container_width=True,
            hide_index=True
        )
    else:
        st.warning("⚠️ La tabla 'data_estudiantes' se conectó pero no contiene registros.")
