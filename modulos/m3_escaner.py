import streamlit as st
import pandas as pd
import numpy as np
import cv2
import re
from supabase import create_client, Client

def iniciar_conexion():
    url = st.secrets["SUPABASE_URL"].strip()
    key = st.secrets["SUPABASE_KEY"].strip()
    return create_client(url, key)

def redimensionar_imagen(img, max_ancho=800):
    alto, ancho = img.shape[:2]
    if ancho > max_ancho:
        proporcion = max_ancho / float(ancho)
        nuevo_alto = int(alto * proporcion)
        return cv2.resize(img, (max_ancho, nuevo_alto), interpolation=cv2.INTER_AREA)
    return img

def alinear_documento(img_original):
    img_segura = redimensionar_imagen(img_original)
    gris = cv2.cvtColor(img_segura, cv2.COLOR_BGR2GRAY)
    desenfoque = cv2.GaussianBlur(gris, (5, 5), 0)
    bordes = cv2.Canny(desenfoque, 75, 200)

    contornos, _ = cv2.findContours(bordes, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contornos: 
        return img_segura, "🔴 No detecté bordes claros."

    contornos = sorted(contornos, key=cv2.contourArea, reverse=True)
    contorno_papel = None

    for c in contornos:
        perimetro = cv2.arcLength(c, True)
        aproximacion = cv2.approxPolyDP(c, 0.02 * perimetro, True)
        if len(aproximacion) == 4:
            contorno_papel = aproximacion
            break

    if contorno_papel is None:
        return img_segura, "🟡 No detecté 4 esquinas claras."

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
        
        proporcion = 1000.0 / max_anchura
        nueva_altura = int(max_altura * proporcion)
        hoja_escaneada = cv2.resize(hoja_escaneada, (1000, nueva_altura))

        return hoja_escaneada, "🟢 Hoja detectada y nivelada con proporciones reales."
    except Exception as e:
        return img_segura, f"🔴 Error matemático de perspectiva: {e}"

def analizar_burbujas(img_aplanada):
    gris = cv2.cvtColor(img_aplanada, cv2.COLOR_BGR2GRAY)
    bin_bordes = cv2.adaptiveThreshold(gris, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 15, 5)
    contornos, _ = cv2.findContours(bin_bordes, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    img_debug = img_aplanada.copy()
    cajas_brutas = []

    for c in contornos:
        x, y, w, h = cv2.boundingRect(c)
        relacion_aspecto = w / float(h)
        
        if y > 250:
            if 12 <= w <= 45 and 12 <= h <= 45:
                if 0.7 <= relacion_aspecto <= 1.3:
                    cajas_brutas.append((x, y, w, h))

    cajas_unicas = []
    for c in cajas_brutas:
        duplicado = False
        for cu in cajas_unicas:
            if abs(c[0]-cu[0]) < 8 and abs(c[1]-cu[1]) < 8:
                duplicado = True
                break
        if not duplicado:
            cajas_unicas.append(c)
            cv2.rectangle(img_debug, (c[0], c[1]), (c[0] + c[2], c[1] + c[3]), (0, 255, 0), 2)

    _, bin_tinta = cv2.threshold(gris, 160, 255, cv2.THRESH_BINARY_INV)

    return bin_tinta, img_debug, cajas_unicas

def ejecutar():
    st.markdown("<h1 style='color: #0d1b2a;'>📷 Central de Escáner y Captura OMR</h1>", unsafe_allow_html=True)
    st.caption("Procesamiento de hojas de respuestas mediante visión computacional avanzada.")

    try:
        supabase = iniciar_conexion()
    except Exception:
        st.error("⚠️ Falla de conexión con el búnker de datos.")
        return

    # 📡 PARACAÍDAS DE INFRAESTRUCTURA MÓDULO 3
    estudiantes_base = []
    pruebas_disponibles = []
    
    try:
        # Intenta jalar los estudiantes (Sabemos que esta sí funciona)
        resultado_est = supabase.table("data_estudiantes").select('ID_Estudiante, Nombre_Completo, Grado, Grupo, "Correo Institucional"').execute()
        estudiantes_base = resultado_est.data
    except Exception as e:
        st.error(f"Falla al cargar matrícula escolar: {e}")

    try:
        # Intenta jalar las pruebas maestras
        resultado_pruebas = supabase.table("pruebas_maestras").select("*").execute()
        pruebas_disponibles = resultado_pruebas.data
    except Exception:
        # 🪂 Si la tabla no existe en producción, no tumba la app. Activa modo vacío.
        st.warning("⚠️ Nota: La tabla 'pruebas_maestras' no ha sido creada en este nuevo proyecto de Supabase.")
        pruebas_disponibles = []

    # Si no hay pruebas creadas, detenemos el flujo amablemente para que las cree en el Módulo 1
    if not pruebas_disponibles:
        st.info("💡 **Próximo Paso Requerido:** Diríjase al menú izquierdo y entre al **'Módulo 1. Creador de Pruebas'** para diseñar su primera evaluación. Al guardarla, la tabla se creará automáticamente en su nuevo proyecto.")
        return

    # --- EL RESTO DEL CÓDIGO OPERA NORMAL SI EXISTEN PRUEBAS ---
    diccionario_pruebas = {f"{p['nombre']} - {p['materia']}": p for p in pruebas_disponibles}
    prueba_activa = st.selectbox("🎯 Seleccione la evaluación que va a calificar:", list(diccionario_pruebas.keys()))
    
    datos_prueba = diccionario_pruebas[prueba_activa]
    llave_maestra = datos_prueba["llave_maestra"]
    total_preguntas = datos_prueba["total_preguntas"]

    with st.expander("👥 VER BASE DE DATOS DE ESTUDIANTES MATRICULADOS", expanded=False):
        if estudiantes_base:
            df_visual_matricula = pd.DataFrame(estudiantes_base).drop_duplicates(subset=["ID_Estudiante"])
            st.dataframe(df_visual_matricula, use_container_width=True, hide_index=True)
