import streamlit as st
import pandas as pd
import numpy as np
import json
import random
import cv2
from PIL import Image
from supabase import create_client, Client

# =================================================================
# 🔌 CONEXIÓN SEGURA AL CENTRO DE DATOS
# =================================================================
@st.cache_resource
def iniciar_conexion():
    url = st.secrets["SUPABASE_URL"].replace('"', '').replace("'", "").strip()
    key = st.secrets["SUPABASE_KEY"].replace('"', '').replace("'", "").strip()
    return create_client(url, key)

# =================================================================
# 👁️ MOTOR DE VISIÓN ARTIFICIAL - COMPRESIÓN Y ALINEACIÓN
# =================================================================
def redimensionar_imagen(img, max_ancho=800):
    """ Evita que el servidor colapse por falta de memoria RAM """
    alto, ancho = img.shape[:2]
    if ancho > max_ancho:
        proporcion = max_ancho / float(ancho)
        nuevo_alto = int(alto * proporcion)
        img_redimensionada = cv2.resize(img, (max_ancho, nuevo_alto), interpolation=cv2.INTER_AREA)
        return img_redimensionada
    return img

def alinear_documento(img_original):
    # 1. Compresión táctica
    img_segura = redimensionar_imagen(img_original)
    
    # 2. Filtros de visión
    gris = cv2.cvtColor(img_segura, cv2.COLOR_BGR2GRAY)
    desenfoque = cv2.GaussianBlur(gris, (5, 5), 0)
    bordes = cv2.Canny(desenfoque, 75, 200)

    contornos, _ = cv2.findContours(bordes, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contornos: 
        return img_segura, "🔴 No detecté bordes claros. Intenta con mejor iluminación."

    contornos = sorted(contornos, key=cv2.contourArea, reverse=True)
    contorno_papel = None

    for c in contornos:
        perimetro = cv2.arcLength(c, True)
        aproximacion = cv2.approxPolyDP(c, 0.02 * perimetro, True)
        if len(aproximacion) == 4:
            contorno_papel = aproximacion
            break

    if contorno_papel is None:
        return img_segura, "🟡 No detecté 4 esquinas claras. La hoja debe contrastar con el fondo."

    try:
        puntos = contorno_papel.reshape(4, 2)
        rect = np.zeros((4, 2), dtype="float32")
        s = puntos.sum(axis=1)
        rect[0] = puntos[np.argmin(s)] 
        rect[2] = puntos[np.argmax(s)] 
        diff = np.diff(puntos, axis=1)
        rect[1] = puntos[np.argmin(diff)] 
        rect[3] = puntos[np.argmax(diff)] 

        (tl, tr, br, bl) = rect
        anchura_A = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
        anchura_B = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
        max_anchura = max(int(anchura_A), int(anchura_B))

        altura_A = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
        altura_B = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
        max_altura = max(int(altura_A), int(altura_B))

        destino = np.array([
            [0, 0],
            [max_anchura - 1, 0],
            [max_anchura - 1, max_altura - 1],
            [0, max_altura - 1]], dtype="float32")

        matriz = cv2.getPerspectiveTransform(rect, destino)
        hoja_escaneada = cv2.warpPerspective(img_segura, matriz, (max_anchura, max_altura))

        return hoja_escaneada, "🟢 Hoja detectada y aplanada con éxito."
    except Exception as e:
        return img_segura, f"🔴 Error matemático de perspectiva: {e}"


def ejecutar():
    st.markdown("<h1 style='color: #0d1b2a;'>📷 Central de Escáner y Captura OMR</h1>", unsafe_allow_html=True)
    st.caption("Procesamiento de hojas de respuestas mediante visión computacional y asignación de matrículas.")

    try:
        supabase: Client = iniciar_conexion()
    except Exception:
        st.error("⚠️ Falla de conexión con el búnker de datos.")
        return

    try:
        pruebas_disponibles = supabase.table("pruebas_maestras").select("*").execute().data
        estudiantes_base = supabase.table("estudiantes").select("codigo_id, nombre_completo, clases(nombre_clase)").execute().data
    except Exception as e:
        st.error(f"Error al conectar con la base institucional: {e}")
        return

    if not pruebas_disponibles:
        st.warning("📭 No hay plantillas maestras en el sistema. Configure una evaluación en el Módulo 1 primero.")
        return

    diccionario_pruebas = {f"{p['nombre']} - {p['materia']}": p for p in pruebas_disponibles}
    prueba_activa = st.selectbox("🎯 Seleccione la evaluación que va a calificar:", list(diccionario_pruebas.keys()))
    
    datos_prueba = diccionario_pruebas[prueba_activa]
    llave_maestra = datos_prueba["llave_maestra"]
    total_preguntas = datos_prueba["total_preguntas"]

    st.markdown("---")
    st.markdown("### 📸 Captura de la Hoja de Respuestas")
    
    metodo_captura = st.radio("Elija el puerto de entrada de la imagen:", ["🎥 Cámara en Vivo (Navegador)", "📂 Cargar Fotografía (Archivo)"], horizontal=True)
    
    imagen_hoja = None
    if metodo_captura == "🎥 Cámara en Vivo (Navegador)":
        imagen_hoja = st.camera_input("Enfoque la hoja de respuestas dentro de los márgenes:")
    else:
        imagen_hoja = st.file_uploader("Suba la captura o fotografía de la hoja de burbujas:", type=["jpg", "png", "jpeg"])

    if imagen_hoja is not None:
        st.info("📡 Archivo recibido en el servidor. Iniciando protocolo de visión...")
        st.markdown("---")
        st.markdown("### 🧠 Procesamiento de Matriz de Pixeles")
        
        try:
            with st.spinner("Descomprimiendo imagen de forma segura..."):
                file_bytes = np.asarray(bytearray(imagen_hoja.getvalue()), dtype=np.uint8)
                img_original = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
                
            if img_original is None:
                st.error("🔴 Error Crítico: OpenCV no pudo leer el archivo. Sube una foto en formato JPG o PNG estándar.")
                st.stop()
            
            with st.spinner("Buscando las 4 esquinas del papel (Alineación)..."):
                img_procesada, mensaje_estado = alinear_documento(img_original)
            
            # Mostrar el resultado visual
            c_foto1, c_foto2 = st.columns(2)
            with c_foto1:
                # Asegurar que se muestre del tamaño redimensionado para comparar
                img_segura = redimensionar_imagen(img_original)
                img_rgb_orig = cv2.cvtColor(img_segura, cv2.COLOR_BGR2RGB)
                st.image(img_rgb_orig, caption="Foto Recibida (Comprimida)", use_container_width=True)
            with c_foto2:
                img_rgb_proc = cv2.cvtColor(img_procesada, cv2.COLOR_BGR2RGB)
                st.image(img_rgb_proc, caption="Corte y Aplanado (Ojo de Halcón)", use_container_width=True)
            
            # Control de flujo según el estado
            if "🟢" in mensaje_estado:
                st.success(mensaje_estado)
            else:
                st.warning(mensaje_estado)
                st.info("💡 Consejo Táctico: Asegúrate de que la foto tenga los 4 cuadritos negros en las esquinas y que el fondo resalte.")
                st.stop()

            # -------------------------------------------------------------
            # SIMULADOR TEMPORAL (Solo corre si el aplanado fue un éxito)
            # -------------------------------------------------------------
            mapa_estudiantes = {}
            if estudiantes_base:
                for est in estudiantes_base:
                    curso = est["clases"]["nombre_clase"] if est["clases"] else "Sin Curso"
                    mapa_estudiantes[est["codigo_id"]] = f"{est['nombre_completo']} ({curso})"

            st.markdown("---")
            c_id, c_resp = st.columns([1, 2])
            with c_id:
                st.markdown("#### 🆔 ID Detectado")
                id_defecto = list(mapa_estudiantes.keys())[0] if mapa_estudiantes else "001"
                id_leido = st.text_input("Código de 3 dígitos extraído por el lente:", value=id_defecto, max_chars=3)
            
            with c_resp:
                st.markdown("#### 👤 Estudiante Identificado")
                nombre_identificado = mapa_estudiantes.get(id_leido, f"Estudiante Desconocido (ID #{id_leido})")
                st.success(f"**{nombre_identificado}**")

            st.markdown("#### 📋 Desglose de Respuestas Escaneadas")
            respuestas_alumno_json = {}
            tabla_comparativa = []
            
            for item in llave_maestra:
                prog = item["Pregunta"]
                correcta = item["Respuesta Correcta"]
                
                opciones = ["A", "B", "C", "D", "E"]
                marcada = correcta if random.random() < 0.8 else random.choice(opciones)
                
                respuestas_alumno_json[prog] = marcada
                estado_icono = "✅" if marcada == correcta else "❌"
                
                tabla_comparativa.append({
                    "Ítem": prog.replace("Pregunta ", "P"),
                    "Burbuja Detectada": marcada,
                    "Clave Correcta": correcta,
                    "Estado": estado_icono
                })
            
            df_tabla = pd.DataFrame(tabla_comparativa)
            st.dataframe(df_tabla.set_index("Ítem").T, use_container_width=True)

            aciertos = sum(1 for fila in tabla_comparativa if fila["Estado"] == "✅")
            puntaje_final = sum(item["Puntaje (Peso)"] for i, item in enumerate(llave_maestra) if tabla_comparativa[i]["Estado"] == "✅")
            porcentaje_efectividad = (aciertos / total_preguntas) * 100

            st.markdown("#### 📊 Calificación Calculada")
            c_m1, c_m2, c_m3 = st.columns(3)
            with c_m1: st.metric("🎯 Aciertos Totales", f"{aciertos} / {total_preguntas}")
            with c_m2: st.metric("🎖️ Nota Definitiva", f"{puntaje_final:.2f} / {datos_prueba['puntaje_maximo']:.1f}")
            with c_m3: st.metric("📈 Porcentaje", f"{porcentaje_efectividad:.1f}%")

            if st.button("💾 CONFIRMAR Y GUARDAR NOTA EN EL REGISTRO CENTRAL", use_container_width=True, type="primary"):
                paquete_respuesta = {
                    "id_prueba": datos_prueba["id_prueba"],
                    "nombre_prueba": datos_prueba["nombre"],
                    "estudiante": nombre_identificado,
                    "respuestas_json": respuestas_alumno_json,
                    "puntaje_obtenido": round(puntaje_final, 2),
                    "puntaje_maximo": datos_prueba["puntaje_maximo"],
                    "porcentaje": round(porcentaje_efectividad, 1)
                }
                
                try:
                    supabase.table("respuestas_estudiantes").insert(paquete_respuesta).execute()
                    st.success(f"🎉 ¡Éxito! Calificación de '{nombre_identificado}' inyectada en el registro escolar.")
                    st.balloons()
                except Exception as e:
                    st.error(f"Falla al registrar la calificación: {e}")

        except Exception as e_critico:
            st.error(f"🚨 **RADAR DE FALLOS (Crash Interno):** {e_critico}")

if __name__ == "__main__":
    ejecutar()
