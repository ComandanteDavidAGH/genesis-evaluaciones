import streamlit as st
import pandas as pd
from supabase import create_client, Client

def iniciar_conexion():
    url = st.secrets["SUPABASE_URL"].strip()
    key = st.secrets["SUPABASE_KEY"].strip()
    return create_client(url, key)

def ejecutar():
    st.markdown("<h1 style='color: #0d1b2a;'>👥 Gestión de Estudiantes</h1>", unsafe_allow_html=True)
    st.caption("Control global de matrícula escolar sincronizado en vivo.")
    st.markdown("---")

    try:
        supabase = iniciar_conexion()
        # Corregido: Se usan comillas dobles para indicarle a la base de datos el espacio del nombre
        resultado = supabase.table("data_estudiantes").select('ID_Estudiante, Nombre_Completo, Grado, Grupo, "Correo Institucional"').execute()
        estudiantes_base = resultado.data
    except Exception as e:
        st.error(f"🚨 Error de enlace seguro: {e}")
        return

    if estudiantes_base:
        df_unicos = pd.DataFrame(estudiantes_base).drop_duplicates(subset=["ID_Estudiante"])
        
        st.metric("📊 Estudiantes Únicos Matriculados", len(df_unicos))
        
        # Despliegue con el nombre exacto de tu columna con espacio
        st.dataframe(
            df_unicos[["ID_Estudiante", "Nombre_Completo", "Grado", "Grupo", "Correo Institucional"]],
            use_container_width=True,
            hide_index=True
        )
    else:
        st.warning("⚠️ La tabla 'data_estudiantes' se conectó pero está vacía internamente.")
