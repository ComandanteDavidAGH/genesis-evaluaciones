import streamlit as st
import pandas as pd
from supabase import create_client, Client

# =================================================================
# 🔌 CONEXIÓN AL CENTRO DE DATOS
# =================================================================
@st.cache_resource
def iniciar_conexion():
    url = st.secrets["SUPABASE_URL"].replace('"', '').replace("'", "").strip()
    key = st.secrets["SUPABASE_KEY"].replace('"', '').replace("'", "").strip()
    return create_client(url, key)

def ejecutar():
    # Título principal corregido
    st.markdown("<h1 style='color: #0d1b2a;'>👥 Gestión de Estudiantes y Cursos</h1>", unsafe_allow_html=True)
    st.caption("Administración centralizada de Cursos, Grupos y Códigos OMR de Estudiantes.")

    try:
        supabase: Client = iniciar_conexion()
    except Exception:
        st.error("⚠️ Falla de conexión con el centro de datos.")
        return

    tab1, tab2 = st.tabs(["🏫 Configurar Cursos / Clases", "👨‍🎓 Registro de Alumnos (Código OMR)"])

    # -----------------------------------------------------------------
    # PESTAÑA 1: GESTIÓN DE CLASES
    # -----------------------------------------------------------------
    with tab1:
        st.markdown("### 🆕 Desplegar Nueva Clase")
        nueva_clase = st.text_input("Nombre de la Clase / Grado:", placeholder="Ej: Grado 11-A")
        
        # Botón corregido sin la palabra búnker
        if st.button("🏗️ Registrar Clase"):
            if nueva_clase:
                try:
                    supabase.table("clases").insert({"nombre_clase": nueva_clase.strip()}).execute()
                    st.success(f"✅ Curso '{nueva_clase}' establecido con éxito.")
                    st.rerun()
                except Exception as e:
                    st.error(f"💥 El curso ya existe o hubo un error: {e}")
            else:
                st.warning("Escriba un nombre válido.")

        st.markdown("---")
        st.markdown("### 📋 Cursos Activos")
        try:
            res_clases = supabase.table("clases").select("*").order("nombre_clase").execute()
            if res_clases.data:
                for c in res_clases.data:
                    st.markdown(f"• **{c['nombre_clase']}**")
            else:
                st.info("No hay clases registradas aún.")
        except Exception as e:
            st.error(f"Error al leer cursos: {e}")

    # -----------------------------------------------------------------
    # PESTAÑA 2: GESTIÓN DE ESTUDIANTES
    # -----------------------------------------------------------------
    with tab2:
        st.markdown("### 📇 Alistar Estudiante en el Sistema")
        try:
            clases_disponibles = supabase.table("clases").select("*").execute().data
        except Exception:
            clases_disponibles = []

        if not clases_disponibles:
            st.warning("⚠️ Debe crear al menos una clase en la pestaña anterior antes de agregar alumnos.")
            return

        opciones_clases = {c["nombre_clase"]: c["id_clase"] for c in clases_disponibles}
        clase_seleccionada = st.selectbox("Asignar al Curso:", list(opciones_clases.keys()))
        
        c_n, c_id = st.columns([2, 1])
        with c_n:
            nombre_alumno = st.text_input("Nombre Completo del Estudiante:")
        with c_id:
            codigo_omr = st.text_input("Código ID (3 Dígitos):", max_chars=3, placeholder="Ej: 358")

        if st.button("🎖️ Guardar y Asignar Código OMR"):
            if nombre_alumno and len(codigo_omr) == 3:
                paquete_alumno = {
                    "codigo_id": codigo_omr.strip(),
                    "nombre_completo": nombre_alumno.strip(),
                    "id_clase": opciones_clases[clase_seleccionada]
                }
                try:
                    supabase.table("estudiantes").insert(paquete_alumno).execute()
                    st.success(f"🎯 Estudiante '{nombre_alumno}' indexado con el ID #{codigo_omr}")
                    st.rerun()
                except Exception as e:
                    st.error(f"💥 Error: El código ID o estudiante ya está registrado. ({e})")
            else:
                st.error("⚠️ Datos inválidos: Asegúrese de poner el nombre y un ID exacto de 3 dígitos.")

        st.markdown("---")
        st.markdown("### 👥 Base de Alumnos Registrados")
        try:
            res_est = supabase.table("estudiantes").select("codigo_id, nombre_completo, clases(nombre_clase)").execute()
            if res_est.data:
                df_est = pd.DataFrame(res_est.data)
                df_est['Curso'] = df_est['clases'].apply(lambda x: x['nombre_clase'] if x else 'Sin Curso')
                df_est = df_est[['codigo_id', 'nombre_completo', 'Curso']]
                df_est.columns = ['Código ID', 'Nombre del Estudiante', 'Curso']
                st.dataframe(df_est.sort_values(by="Curso"), use_container_width=True, hide_index=True)
            else:
                st.info("No hay alumnos alistados en la base de datos.")
        except Exception as e:
            st.error(f"Error al cargar la bitácora: {e}")

if __name__ == "__main__":
    ejecutar()
