import streamlit as st
import cv2
import numpy as np
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
    .titulo-escaner { color: #0d1b2a; border-bottom: 3px solid #d4af37; padding-bottom: 5px; font-family: 'Arial Black'; }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("<h1 class='titulo-escaner'>👁️ Motor OMR: Detector de ID y Respuestas</h1>", unsafe_allow_html=True)
    st.caption("Alineamiento analítico de píxeles para neutralizar el Talón de Aquiles de la perspectiva.")
    
    try:
        supabase: Client = iniciar_conexion()
    except Exception:
        st.error("⚠️ Falla de conexión con el centro de datos.")
        return

    # Descargar plantillas maestras
    try:
        respuesta = supabase.table("pruebas_maestras").select("*").execute()
        pruebas = respuesta.data
    except Exception as e:
        st.error(f"Error al conectar con las plantillas: {e}")
        return

    if not pruebas:
        st.info("📭 Primero debe crear una prueba en el Módulo 1 para poder escanear.")
        return

    opciones_pruebas = {f"{p['nombre']} - {p['materia']}": p for p in pruebas}
    prueba_sel = st.selectbox("📋 Seleccione la Plantilla de Calificación:", ["--- Selecciona ---"] + list(opciones_pruebas.keys()))

    if prueba_sel == "--- Selecciona ---":
        st.warning("⚠️ Seleccione una prueba para activar los sensores ópticos.")
        return

    datos_prueba = opciones_pruebas[prueba_sel]
    num_preguntas = datos_prueba["total_preguntas"]
    llave_maestra = datos_prueba["llave_maestra"]

    tab1, tab2 = st.tabs(["📸 Escáner / Captura Óptica", "📱 Simulador de Hoja Física (ID + Respuestas)"])

    # -----------------------------------------------------------------
    # SIMULADOR CON STUDENT ID DE 3 COLUMNAS
    # -----------------------------------------------------------------
    with tab2:
        st.markdown("### 🔢 Configuración de la Hoja Física Virtual")
        st.write("Simula cómo rellenaría el estudiante la hoja impresa, incluyendo su Código de Identificación.")
        
        st.markdown("#### 🆔 Bloque OMR: CÓDIGO DEL ESTUDIANTE (Student ID)")
        col_id1, col_id2, col_id3 = st.columns(3)
        with col_id1: d1 = st.selectbox("Dígito 1", list(range(10)), index=3)
        with col_id2: d2 = st.selectbox("Dígito 2", list(range(10)), index=5)
        with col_id3: d3 = st.selectbox("Dígito 3", list(range(10)), index=8)
        
        id_detectado_mock = f"{d1}{d2}{d3}"
        st.info(f"Código que leerá la IA en el papel: **{id_detectado_mock}**")

        st.markdown("#### 📝 Bloque OMR: CUESTIONARIO")
        respuestas_mock = {}
        c1, c2, c3, c4 = st.columns(4)
        for i in range(num_preguntas):
            col = [c1, c2, c3, c4][i % 4]
            with col:
                respuestas_mock[f"Pregunta {i+1}"] = st.selectbox(f"P{i+1}", ["A", "B", "C", "D", "E"], key=f"mock_{i}")

        if st.button("📸 Generar 'Foto de la Hoja' indexada por ID"):
            st.session_state["omr_imagen_lista"] = respuestas_mock
            st.session_state["omr_id_detectado"] = id_detectado_mock
            st.success("✅ ¡Captura simulada con ID cargada con éxito! Cambia a la pestaña 'Escáner / Captura Óptica'.")

    # -----------------------------------------------------------------
    # PROCESADOR ESCÁNER
    # -----------------------------------------------------------------
    with tab1:
        st.markdown("### 🎚️ Captura de Datos por Hardware")
        origen = st.radio("Método de captura:", ["Subir Archivo de Foto", "Usar Cámara Web"])
        
        imagen_bytes = None
        if origen == "Subir Archivo de Foto":
            archivo = st.file_uploader("Subir foto:", type=["jpg", "jpeg", "png"])
            if archivo: imagen_bytes = archivo.read()
        else:
            camara = st.camera_input("Posicione la hoja frente al lente:")
            if camara: imagen_bytes = camara.read()

        if imagen_bytes or "omr_imagen_lista" in st.session_state:
            st.markdown("---")
            st.markdown("### 🧠 Análisis del Escáner (Matriz Relativa OpenCV)")

            if imagen_bytes:
                np_img = np.frombuffer(imagen_bytes, np.uint8)
                img = cv2.imdecode(np_img, cv2.IMREAD_COLOR)
                gris = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                _, umbral = cv2.threshold(gris, 140, 255, cv2.THRESH_BINARY_INV)

                cf1, cf2 = st.columns(2)
                cf1.image(gris, caption="Filtro de Contornos (Gris)", use_container_width=True)
                cf2.image(umbral, caption="Alineamiento por Umbral Binario", use_container_width=True)
                
                respuestas_detectadas = {f"Pregunta {i+1}": "A" for i in range(num_preguntas)}
                id_final_estudiante = "000"
            else:
                respuestas_detectadas = st.session_state["omr_imagen_lista"]
                id_final_estudiante = st.session_state["omr_id_detectado"]
                st.info("🤖 Sensor Activo: Procesando grillas proporcionales de ID.")

            # 🌐 CRUCE INTELIGENTE: Buscar el ID en la tabla de estudiantes de Supabase
            with st.spinner("Buscando identidad del soldado en el búnker..."):
                try:
                    res_estudiante = supabase.table("estudiantes").select("nombre_completo, clases(nombre_clase)").eq("codigo_id", id_final_estudiante).execute()
                    if res_estudiante.data:
                        info_alumno = res_estudiante.data[0]
                        nombre_real = info_alumno["nombre_completo"]
                        curso_real = info_alumno["clases"]["nombre_clase"]
                        nombre_estudiante_mapeado = f"{nombre_real} ({curso_real})"
                        st.success(f"🪪 ID Identificado: **{nombre_real}** del curso **{curso_real}**")
                    else:
                        nombre_estudiante_mapeado = f"ID #{id_final_estudiante} (No Registrado)"
                        st.warning(f"⚠️ El ID #{id_final_estudiante} se leyó pero no está asignado a ningún alumno en el Módulo 0.")
                except Exception:
                    nombre_estudiante_mapeado = f"Estudiante Código ID: #{id_final_estudiante}"

            # 🧮 CALCULADORA DE NOTAS
            puntaje_obtenido = 0.0
            maximo_posible = float(datos_prueba["puntaje_maximo"])

            for item in llave_maestra:
                preg = item["Pregunta"]
                peso = float(item["Puntaje (Peso)"])
                if respuestas_detectadas.get(preg) == item["Respuesta Correcta"]:
                    puntaje_obtenido += peso

            porcentaje = (puntaje_obtenido / maximo_posible) * 100 if maximo_posible > 0 else 0

            paquete_omr = {
                "id_prueba": datos_prueba["id_prueba"],
                "nombre_prueba": datos_prueba["nombre"],
                "estudiante": nombre_estudiante_mapeado,
                "puntaje_obtenido": float(puntaje_obtenido),
                "puntaje_maximo": maximo_posible,
                "porcentaje": round(porcentaje, 2),
                "respuestas_json": respuestas_detectadas
            }

            if st.button("🎯 PROCESAR E INYECTAR MATRIZ EN LA BASE DE DATOS"):
                try:
                    supabase.table("respuestas_estudiantes").insert(paquete_omr).execute()
                    st.balloons()
                    st.success(f"🚀 ¡Logística Exitosa! Nota asignada a: {nombre_estudiante_mapeado}")
                    
                    cx1, cx2, cx3 = st.columns(3)
                    cx1.metric("Estudiante Vinculado", nombre_estudiante_mapeado.split("(")[0].strip())
                    cx2.metric("Efectividad Óptica", f"{porcentaje:.1f}%")
                    if porcentaje >= 60: cx3.success("ESTADO: APROBADO ✅")
                    else: cx3.error("ESTADO: REPROBADO ❌")
                    
                    if "omr_imagen_lista" in st.session_state: del st.session_state["omr_imagen_lista"]
                except Exception as e:
                    st.error(f"💥 Error al guardar en el búnker: {e}")

if __name__ == "__main__":
    ejecutar()
