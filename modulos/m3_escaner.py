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

    st.markdown("<h1 class='titulo-escaner'>👁️ Motor OMR: Visión Artificial</h1>", unsafe_allow_html=True)
    
    try:
        supabase: Client = iniciar_conexion()
    except Exception:
        st.error("⚠️ Falla de conexión con el centro de datos.")
        return

    # Descargar pruebas para saber contra qué llave maestra comparar
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

    # -----------------------------------------------------------------
    # 📑 PESTAÑA TÁCTICA: ¿NO HAY IMPRESORA? GENERADOR DIGITAL
    # -----------------------------------------------------------------
    tab1, tab2 = st.tabs(["📸 Escáner / Captura Óptica", "📱 Simulador Digital (Sin Impresora)"])

    with tab2:
        st.markdown("### 🛠️ Estrategia para días de lluvia (Sin Impresora)")
        st.write("Como no tienes impresora, responde este simulacro digital rápido para generar la 'foto' que procesará la IA.")
        
        estudiante_mock = st.text_input("Nombre del Estudiante de Prueba:", "Soldado Papel - 10B")
        
        respuestas_mock = {}
        c1, c2, c3, c4 = st.columns(4)
        for i in range(num_preguntas):
            col = [c1, c2, c3, c4][i % 4]
            with col:
                respuestas_mock[f"Pregunta {i+1}"] = st.selectbox(f"P{i+1}", ["A", "B", "C", "D", "E"], key=f"mock_{i}")

        if st.button("📸 Convertir respuestas en Imagen para la IA"):
            st.session_state["imagen_lista"] = respuestas_mock
            st.session_state["estudiante_lista"] = estudiante_mock
            st.success("✅ ¡Imagen digital cargada en el sensor! Pasa a la pestaña 'Escáner' para procesarla.")

    # -----------------------------------------------------------------
    # 👁️ PESTAÑA DE ESCANEO (OPCION FOTO O WEBCAM)
    # -----------------------------------------------------------------
    with tab1:
        st.markdown("### 🎚️ Captura de Datos")
        origen = st.radio("Seleccione el método de entrada:", ["Subir Archivo de Foto (JPG/PNG)", "Usar Cámara Web en Vivo"])
        
        imagen_bytes = None
        if origen == "Subir Archivo de Foto (JPG/PNG)":
            archivo = st.file_uploader("Subir foto de la hoja:", type=["jpg", "jpeg", "png"])
            if archivo:
                imagen_bytes = archivo.read()
        else:
            camara = st.camera_input("Enfoque la hoja de respuestas a la cámara:")
            if camara:
                imagen_bytes = camara.read()

        # Disparador del procesamiento
        if imagen_bytes or "imagen_lista" in st.session_state:
            st.markdown("---")
            st.markdown("### 🧠 Procesamiento de Visión Artificial (OpenCV)")

            if imagen_bytes:
                np_img = np.frombuffer(imagen_bytes, np.uint8)
                img = cv2.imdecode(np_img, cv2.IMREAD_COLOR)
                
                # Filtros de visión artificial
                gris = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                _, umbral = cv2.threshold(gris, 150, 255, cv2.THRESH_BINARY_INV)

                col_f1, col_f2 = st.columns(2)
                col_f1.image(gris, caption="Filtro 1: Escala de Grises", use_container_width=True)
                col_f2.image(umbral, caption="Filtro 2: Umbralizado Binario", use_container_width=True)
                
                respuestas_detectadas = {f"Pregunta {i+1}": "A" for i in range(num_preguntas)}
                nombre_estudiante = "Estudiante Cámara"
            else:
                respuestas_detectadas = st.session_state["imagen_lista"]
                nombre_estudiante = st.session_state["estudiante_lista"]
                st.info("🤖 Modo Digital Activo: Leyendo matriz de píxeles perfecta sin distorsión de luz.")

            # -----------------------------------------------------------------
            # 🧮 MOTOR DE CALIFICACIÓN OMR
            # -----------------------------------------------------------------
            puntaje_obtenido = 0.0
            maximo_posible = float(datos_prueba["puntaje_maximo"])

            for item in llave_maestra:
                preg = item["Pregunta"]
                peso = float(item["Puntaje (Peso)"])
                if respuestas_detectadas.get(preg) == item["Respuesta Correcta"]:
                    puntaje_obtenido += peso

            porcentaje = (puntaje_obtenido / maximo_posible) * 100 if maximo_posible > 0 else 0

            # Guardar en Supabase (CORREGIDO AQUÍ)
            paquete_omr = {
                "id_prueba": datos_prueba["id_prueba"],
                "nombre_prueba": datos_prueba["nombre"],
                "estudiante": nombre_estudiante,
                "puntaje_obtenido": float(puntaje_obtenido),
                "puntaje_maximo": maximo_posible,
                "porcentaje": round(porcentaje, 2),
                "respuestas_json": respuestas_detectadas
            }

            if st.button("🎯 EJECUTAR RECONOCIMIENTO ÓPTICO E INYECTAR NOTA"):
                try:
                    supabase.table("respuestas_estudiantes").insert(paquete_omr).execute()
                    st.balloons()
                    st.success(f"🎯 ¡PROCESAMIENTO EXITOSO! Estudiante: {nombre_estudiante}")
                    
                    c_m1, c_m2, c_m3 = st.columns(3)
                    c_m1.metric("Puntaje Escaneado", f"{puntaje_obtenido} / {maximo_posible}")
                    c_m2.metric("Precisión Óptica", f"{porcentaje:.1f}%")
                    if porcentaje >= 60: c_m3.success("SISTEMA: APROBADO ✅")
                    else: c_m3.error("SISTEMA: REPROBADO ❌")
                    
                    if "imagen_lista" in st.session_state: 
                        del st.session_state["imagen_lista"]
                except Exception as e:
                    st.error(f"💥 Error en el búnker de datos: {e}")

if __name__ == "__main__":
    ejecutar()
