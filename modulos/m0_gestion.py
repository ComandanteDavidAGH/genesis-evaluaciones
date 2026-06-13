import streamlit as st
import pandas as pd
from supabase import create_client, Client

# =================================================================
# 📡 ENLACE DIRECTO SIN INTERMEDIARIOS (Bypasando Secrets corruptos)
# =================================================================
def iniciar_conexion():
    # URL de tu proyecto real (sacado de la telemetría de tu foto)
    url = "https://bwrwkluhzzmrzrsszwac.supabase.co" 
    
    # PEGA AQUÍ TU LLAVE ANONpUBLIC REAL ENTRE LAS COMILLAS
    key = "TU_LLAVE_ANON_PUBLIC_REAL_AQUÍ" 
    
    return create_client(url, key)

def ejecutar():
    st.markdown("<h1 style='color: #0d1b2a;'>👥 Gestión de Estudiantes</h1>", unsafe_allow_html=True)
    st.caption("Control global de matrícula escolar sincronizado en vivo.")
    st.markdown("---")

    try:
        supabase = iniciar_conexion()
        # Buscamos con el nombre exacto de tu tabla en Supabase: data_estudiantes
        resultado = supabase.table("data_estudiantes").select("ID_Estudiante, Nombre_Completo, Grado, Grupo, Correo_Institucional").execute()
        estudiantes_base = resultado.data
    except Exception as e:
        st.error(f"🚨 Error de enlace con 'data_estudiantes': {e}")
        return

    if estudiantes_base:
        df_unicos = pd.DataFrame(estudiantes_base).drop_duplicates(subset=["ID_Estudiante"])
        
        st.metric("📊 Estudiantes Únicos Matriculados", len(df_unicos))
        
        st.dataframe(
            df_unicos[["ID_Estudiante", "Nombre_Completo", "Grado", "Grupo", "Correo_Institucional"]],
            use_container_width=True,
            hide_index=True
        )
    else:
        st.warning("⚠️ La tabla 'data_estudiantes' se conectó pero está vacía internamente.")
