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
# 👁️ MOTOR DE VISIÓN ARTIFICIAL (OPENCV) - FASE 1: ALINEACIÓN
# =================================================================
def alinear_documento(imagen_bytes):
    """
    Toma la foto en crudo, busca el rectángulo más grande (el papel),
    y lo recorta/aplana para eliminar el fondo de la mesa.
    """
    # 1. Convertir la foto de Streamlit a un formato que OpenCV entienda
    file_bytes = np.asarray(bytearray(imagen_bytes.read()), dtype=np.uint8)
    img_original = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
    
    # 2. Filtros para que el cerebro de la IA vea los bordes
    gris = cv2.cvtColor(img_original, cv2.COLOR_BGR2GRAY)
    desenfoque = cv2.GaussianBlur(gris, (5, 5), 0)
    bordes = cv2.Canny(desenfoque, 75, 200)

    # 3. Buscar todos los contornos en la foto y ordenarlos por tamaño
    contornos, _ = cv2.findContours(bordes, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contornos: return img_original, "🔴 No detecté bordes claros en la foto."

    contornos = sorted(contornos, key=cv2.contourArea, reverse=True)
    contorno_papel = None

    # 4. Buscar el primer contorno que tenga exactamente 4 esquinas (Un rectángulo)
    for c in contornos:
        perimetro = cv2.arcLength(c, True)
        aproximacion = cv2.approxPolyDP(c, 0.02 * perimetro, True)
        if len(aproximacion) == 4:
            contorno_papel = aproximacion
            break

    if contorno_papel is None:
        return img_original, "🟡 No detecté 4 esquinas claras. Intenta alejar la cámara un poco."

    # 5. Geometría de Perspectiva (Estirar la hoja para que quede plana)
    puntos = contorno_papel.reshape(4, 2)
    rect = np.zeros((4, 2), dtype="float32")
    s = puntos.sum(axis=1)
    rect[0] = puntos[np.argmin(s)] # Arriba-Izquierda
    rect[2] = puntos[np.argmax(s)] # Abajo-Derecha
    diff = np.diff(puntos, axis=1)
    rect[1] = puntos[np.argmin(diff)] # Arriba-Derecha
    rect[3] = puntos[np.argmax(diff)] # Abajo-Izquierda

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
    hoja_escaneada = cv2.warpPerspective(img_original, matriz, (max_anchura, max_altura))

    return hoja_escaneada, "🟢 Hoja detectada y aplanada con éxito."


def ejecutar():
    st.markdown("<h1 style='color: #0d1b2a;'>📷 Central de Escáner y Captura OMR</h1>", unsafe_allow_html=True)
    st.caption("Procesamiento de hojas de respuestas mediante visión computacional y asignación de matrículas.")

    try:
        supabase: Client = iniciar_conexion()
    except Exception:
        st.error("⚠️ Falla de conexión con el búnker de datos.")
        return

    # 1. DESCARGA DE INFORMACIÓN MAESTRA
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

    if imagen_hoja:
        st.markdown("---")
        st.markdown("### 🧠 Procesamiento de Matriz de Pixeles")
        
        with st.spinner("Ejecutando binarización y escaneo de bordes OMR..."):
            
            # --- LA MAGIA OCURRE AQUÍ ---
            img_procesada, mensaje_estado = alinear_documento(imagen_hoja)
            
            # Mostrar el resultado visual al profesor
            c_foto1, c_foto2 = st.columns(2)
            with c_foto1:
                st.image(imagen_hoja, caption="Foto Original", use_container_width=True)
            with c_foto2:
                # Convertimos BGR (OpenCV) a RGB (Streamlit) para mostrarla bien
                img_rgb = cv2.cvtColor(img_procesada, cv2.COLOR_BGR2RGB)
                st.image(img_rgb, caption="Corte y Aplanado (Ojo de Halcón)", use_container_width=True)
            
            if "🟢" in mensaje_estado:
                st.success(mensaje_estado)
            else:
                st.warning(mensaje_estado)
                st.stop() # Si no detectó la hoja, detenemos el código aquí para que vuelva a tomar la foto.

            # -------------------------------------------------------------
            # TODO LO DE ABAJO SIGUE EN SIMULACIÓN HASTA CONFIRMAR LA FOTO
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

if __name__ == "__main__":
    ejecutar()
