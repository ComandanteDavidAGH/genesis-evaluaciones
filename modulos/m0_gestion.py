import streamlit as st
import pandas as pd
import re
from supabase import create_client, Client

# =================================================================
# 📡 ENLACE DIRECTO CON PURIFICADOR DE CARACTERES OCULTOS
# =================================================================
def iniciar_conexion():
    url = "https://bwrwkluhzzmrzrsszwac.supabase.co" 
    
    # ⬇️ PEGA TU CLAVE LARGA AQUÍ ADENTRO ⬇️
    key_sucia = "TU_LLAVE_ANON_PUBLIC_REAL_AQUÍ" 
    
    # El escudo: Borra automáticamente acentos, espacios, \xcd y cualquier símbolo raro
    key_limpia = re.sub(r'[^A-Za-z0-9._-]', '', key_sucia)
    
    return create_client(url, key_limpia)

def ejecutar():
    st.markdown("<h1 style='color: #0d1b2a;'>👥 Gestión de Estudiantes</h1>", unsafe_allow_html=True)
    st.caption("Control global de matrícula escolar sincronizado en vivo.")
    st.markdown("---")

    try:
        supabase = iniciar_conexion()
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
