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
    st.markdown("<h1 style='color: #0d1b2a;'>👥 Registro y Gestión de Estudiantes</h1>", unsafe_allow_html=True)
    st.caption("Administración centralizada de Cursos, Grupos e Importación Masiva de Matrículas.")

    try:
        supabase: Client = iniciar_conexion()
    except Exception:
        st.error("⚠️ Falla de conexión con el centro de datos.")
        return

    tab1, tab2, tab3 = st.tabs([
        "🏫 Configurar Cursos / Clases", 
        "👨‍🎓 Registro Individual", 
        "📂 Carga Masiva (Excel / CSV)"
    ])

    try:
        clases_disponibles = supabase.table("clases").select("*").order("nombre_clase").execute().data
    except Exception:
        clases_disponibles = []

    opciones_clases = {c["nombre_clase"]: c["id_clase"] for c in clases_disponibles}

    # -----------------------------------------------------------------
    # PESTAÑA 1: GESTIÓN DE CLASES
    # -----------------------------------------------------------------
    with tab1:
        st.markdown("### 🆕 Desplegar Nueva Clase o Grado")
        nueva_clase = st.text_input("Nombre de la Clase / Grado:", placeholder="Ej: Grado 11-A")
        
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
        st.markdown("### 📋 Cursos Activos en la Institución")
        if clases_disponibles:
            for c in clases_disponibles:
                st.markdown(f"• **{c['nombre_clase']}**")
        else:
            st.info("No hay clases registradas aún.")

    # -----------------------------------------------------------------
    # PESTAÑA 2: REGISTRO INDIVIDUAL
    # -----------------------------------------------------------------
    with tab2:
        st.markdown("### 📇 Alistar Estudiante Manualmente")
        if not clases_disponibles:
            st.warning("⚠️ Debe crear al menos una clase en la pestaña anterior antes de registrar alumnos.")
        else:
            clase_seleccionada = st.selectbox("Asignar al Curso:", list(opciones_clases.keys()), key="individual_clase")
            
            c_n, c_id = st.columns([2, 1])
            with c_n:
                nombre_alumno = st.text_input("Nombre Completo del Estudiante:")
            with c_id:
                codigo_omr = st.text_input("Código ID (3 Dígitos):", max_chars=3, placeholder="Ej: 358")

            if st.button("🎖️ Guardar Estudiante"):
                if nombre_alumno and len(codigo_omr) == 3 and codigo_omr.isdigit():
                    paquete_alumno = {
                        "codigo_id": codigo_omr.strip(),
                        "nombre_completo": nombre_alumno.strip(),
                        "id_clase": opciones_clases[clase_seleccionada]
                    }
                    try:
                        supabase.table("estudiantes").insert(paquete_alumno).execute()
                        st.success(f"🎯 Estudiante '{nombre_alumno}' registrado con el ID #{codigo_omr}")
                        st.rerun()
                    except Exception as e:
                        st.error(f"💥 Error: El código ID ya pertenece a otro estudiante. ({e})")
                else:
                    st.error("⚠️ Datos inválidos: Ingrese el nombre y un ID numérico exacto de 3 dígitos.")

    # -----------------------------------------------------------------
    # PESTAÑA 3: CARGA MASIVA (INTERFAZ PREMIUM REFINADA)
    # -----------------------------------------------------------------
    with tab3:
        st.markdown("### 📊 Importación Masiva en Ráfaga")
        st.write("Cargue listados institucionales para automatizar la asignación de matrículas y códigos OMR.")
        
        if not clases_disponibles:
            st.warning("⚠️ Configure un curso antes de habilitar el puerto de carga masiva.")
        else:
            clase_masiva = st.selectbox("Asignar todo el listado al Curso:", list(opciones_clases.keys()), key="masiva_clase")
            
            # Ajuste de control estético: Preguntar por la estructura del archivo
            tiene_encabezado = st.toggle("📌 El archivo incluye una fila de títulos (Encabezado)", value=False)
            
            archivo_cargado = st.file_uploader("Arrastre aquí el archivo de Excel o CSV:", type=["xlsx", "csv"])
            
            if archivo_cargado:
                try:
                    header_value = 0 if tiene_encabezado else None
                    
                    if archivo_cargado.name.endswith('.xlsx'):
                        df = pd.read_excel(archivo_cargado, header=header_value)
                    else:
                        df = pd.read_csv(archivo_cargado, header=header_value)
                    
                    # Si no tiene encabezados, asignamos nombres estéticos temporales
                    if not tiene_encabezado:
                        df.columns = [f"Columna {i+1}" for i in range(len(df.columns))]
                    
                    st.markdown("---")
                    st.markdown("#### 👁️ Vista Previa del Documento")
                    
                    # Tarjeta de estado estética
                    st.metric("📋 Registros encontrados en el archivo", f"{len(df)} Alumnos")
                    
                    st.dataframe(df, use_container_width=True, hide_index=True)
                    
                    st.markdown("#### 🔗 Mapeo de Datos")
                    columna_nombres = st.selectbox("Seleccione la columna que contiene los Nombres de los Estudiantes:", df.columns)
                    
                    if st.button("🚀 PROCESAR MATRÍCULA E INYECTAR LISTADO"):
                        res_ids = supabase.table("estudiantes").select("codigo_id").execute()
                        ids_ocupados = {int(row["codigo_id"]) for row in res_ids.data if row["codigo_id"].isdigit()}
                        
                        estudiantes_a_insertar = []
                        id_actual_secuencial = 1
                        
                        listado_nombres = df[columna_nombres].dropna().astype(str).tolist()
                        
                        for nombre in listado_nombres:
                            if not nombre.strip():
                                continue
                                
                            while id_actual_secuencial in ids_ocupados:
                                id_actual_secuencial += 1
                            
                            if id_actual_secuencial > 999:
                                st.error("💥 Falla crítica: Se ha superado el límite de 999 estudiantes.")
                                return
                                
                            codigo_generado_str = f"{id_actual_secuencial:03d}"
                            ids_ocupados.add(id_actual_secuencial)
                            
                            estudiantes_a_insertar.append({
                                "codigo_id": codigo_generado_str,
                                "nombre_completo": nombre.strip(),
                                "id_clase": opciones_clases[clase_masiva]
                            })
                        
                        if estudiantes_a_insertar:
                            with st.spinner("Inyectando registros en bloque..."):
                                supabase.table("estudiantes").insert(estudiantes_a_insertar).execute()
                            st.balloons()
                            st.success(f"🎉 Registro exitoso: Se han matriculado {len(estudiantes_a_insertar)} estudiantes en {clase_masiva}.")
                            st.rerun()
                        else:
                            st.warning("El archivo no contenía nombres válidos para procesar.")
                            
                except Exception as e:
                    st.error(f"Error al analizar el archivo: {e}")

    # -----------------------------------------------------------------
    # VISUALIZACIÓN GENERAL DEL ALUMNADO
    # -----------------------------------------------------------------
    st.markdown("---")
    st.markdown("### 👥 Base de Datos Global de Estudiantes")
    try:
        res_est = supabase.table("estudiantes").select("codigo_id, nombre_completo, clases(nombre_clase)").execute()
        if res_est.data:
            df_est = pd.DataFrame(res_est.data)
            df_est['Curso'] = df_est['clases'].apply(lambda x: x['nombre_clase'] if x else 'Sin Curso')
            df_est = df_est[['codigo_id', 'nombre_completo', 'Curso']]
            df_est.columns = ['Código ID', 'Nombre del Estudiante', 'Curso']
            st.dataframe(df_est.sort_values(by=["Curso", "Nombre del Estudiante"]), use_container_width=True, hide_index=True)
        else:
            st.info("No hay estudiantes registrados en la base de datos institucional.")
    except Exception as e:
        st.error(f"Error al cargar la bitácora: {e}")

if __name__ == "__main__":
    ejecutar()
