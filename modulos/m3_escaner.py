import streamlit as st
import pandas as pd
import numpy as np
import json
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
# 👁️ MOTOR DE VISIÓN ARTIFICIAL (ALINEACIÓN Y RAYOS X)
# =================================================================
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

        destino = np.array([
            [0, 0],
            [800 - 1, 0],
            [800 - 1, 1100 - 1],
            [0, 1100 - 1]], dtype="float32")

        matriz = cv2.getPerspectiveTransform(rect, destino)
        hoja_escaneada = cv2.warpPerspective(img_segura, matriz, (800, 1100))
        return hoja_escaneada, "🟢 Hoja detectada y estirada al 100% con éxito."
    except Exception as e:
        return img_segura, f"🔴 Error matemático de perspectiva: {e}"

def analizar_burbujas(img_aplanada):
    gris = cv2.cvtColor(img_aplanada, cv2.COLOR_BGR2GRAY)
    binarizada = cv2.adaptiveThreshold(gris, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)
    contornos, _ = cv2.findContours(binarizada, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    img_debug = img_aplanada.copy()
    cajas_encontradas = []

    for c in contornos:
        area = cv2.contourArea(c)
        x, y, w, h = cv2.boundingRect(c)
        relacion_aspecto = w / float(h)
        
        if 15 <= w <= 40 and 15 <= h <= 40:
            if 0.8 <= relacion_aspecto <= 1.2:
                perimetro = cv2.arcLength(c, True)
                if perimetro > 0:
                    circularidad = 4 * np.pi * (area / (perimetro * perimetro))
                    if 0.6 <= circularidad <= 1.2:
                        cajas_encontradas.append((x, y, w, h))
                        cv2.rectangle(img_debug, (x, y), (x + w, y + h), (0, 255, 0), 2)

    return binarizada, img_debug, cajas_encontradas

# =================================================================
# 🖥️ INTERFAZ DE USUARIO Y EJECUCIÓN
# =================================================================
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
        st.info("📡 Archivo recibido. Iniciando protocolo de visión avanzada...")
        st.markdown("---")
        
        try:
            with st.spinner("Alineando geometría del documento..."):
                file_bytes = np.asarray(bytearray(imagen_hoja.getvalue()), dtype=np.uint8)
                img_original = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
                
                if img_original is None:
                    st.error("🔴 Error Crítico: OpenCV no pudo leer el archivo.")
                    st.stop()
                
                img_aplanada, mensaje_estado = alinear_documento(img_original)
            
            if "🟢" not in mensaje_estado:
                st.warning(mensaje_estado)
                st.stop()

            # --- FASE 2: DETECCIÓN Y CALIFICACIÓN REAL ---
            with st.spinner("Ejecutando escáner de Rayos X y calificando respuestas..."):
                img_rayos_x, img_analisis, cajas = analizar_burbujas(img_aplanada)
                
                # 1. Eliminar burbujas duplicadas (a veces el escáner ve el borde interno y externo)
                cajas_unicas = []
                for c in cajas:
                    duplicado = False
                    for cu in cajas_unicas:
                        if abs(c[0]-cu[0]) < 5 and abs(c[1]-cu[1]) < 5:
                            duplicado = True
                            break
                    if not duplicado:
                        cajas_unicas.append(c)
                
                # 2. Separar zona de ID (izquierda) y zona de Respuestas (derecha)
                cajas_respuestas = [c for c in cajas_unicas if c[0] > 300]
                
                # 3. Ordenar las respuestas por filas (Eje Y)
                cajas_respuestas.sort(key=lambda b: b[1])
                filas = []
                if len(cajas_respuestas) > 0:
                    fila_actual = [cajas_respuestas[0]]
                    for caja in cajas_respuestas[1:]:
                        if abs(caja[1] - fila_actual[0][1]) < 15: # Tolerancia de 15 píxeles de desviación horizontal
                            fila_actual.append(caja)
                        else:
                            filas.append(fila_actual)
                            fila_actual = [caja]
                    filas.append(fila_actual)
                
                # 4. Leer las respuestas marcadas
                respuestas_detectadas = []
                opciones = ["A", "B", "C", "D", "E"]
                
                for fila in filas:
                    fila.sort(key=lambda b: b[0]) # Ordenar de izquierda a derecha (Eje X)
                    # Agrupar de 5 en 5 (Las opciones de cada pregunta)
                    for i in range(0, len(fila), 5):
                        grupo = fila[i:i+5]
                        if len(grupo) == 5:
                            max_pixeles = 0
                            idx_marcado = -1
                            
                            for j, (x, y, w, h) in enumerate(grupo):
                                # Recorte central (Core) para evitar contar el anillo impreso
                                roi = img_rayos_x[y+4:y+h-4, x+4:x+w-4]
                                pixeles_blancos = cv2.countNonZero(roi)
                                
                                if pixeles_blancos > max_pixeles:
                                    max_pixeles = pixeles_blancos
                                    idx_marcado = j
                            
                            # Umbral táctico: Mínimo de 15 píxeles para considerar que hay lápiz y no es una mancha
                            if max_pixeles > 15:
                                respuestas_detectadas.append(opciones[idx_marcado])
                            else:
                                respuestas_detectadas.append("BLANCO")

            st.success("✅ **¡Documento escaneado y procesado exitosamente por la Inteligencia Artificial!**")

            # -------------------------------------------------------------
            # HUD DE RESULTADOS Y GUARDADO
            # -------------------------------------------------------------
            mapa_estudiantes = {}
            if estudiantes_base:
                for est in estudiantes_base:
                    curso = est["clases"]["nombre_clase"] if est["clases"] else "Sin Curso"
                    mapa_estudiantes[est["codigo_id"]] = f"{est['nombre_completo']} ({curso})"

            st.markdown("---")
            c_id, c_resp = st.columns([1, 2])
            with c_id:
                st.markdown("#### 🆔 ID del Estudiante")
                id_defecto = list(mapa_estudiantes.keys())[0] if mapa_estudiantes else "001"
                id_leido = st.text_input("Verifique o digite el Código:", value=id_defecto, max_chars=3)
            
            with c_resp:
                st.markdown("#### 👤 Identidad Confirmada")
                nombre_identificado = mapa_estudiantes.get(id_leido, f"Estudiante Desconocido (ID #{id_leido})")
                if "Desconocido" in nombre_identificado:
                    st.error(f"**{nombre_identificado}**")
                else:
                    st.success(f"**{nombre_identificado}**")

            st.markdown("#### 📋 Desglose Oficial de Respuestas Extraídas")
            respuestas_alumno_json = {}
            tabla_comparativa = []
            aciertos = 0
            puntaje_final = 0.0
            
            # Cruzar lo que leyó la IA contra la Llave Maestra
            for idx, item in enumerate(llave_maestra):
                prog = item["Pregunta"]
                correcta = item["Respuesta Correcta"]
                peso = float(item["Puntaje (Peso)"])
                
                # Proteger contra hojas mal escaneadas donde no se leyeron todas las preguntas
                marcada = respuestas_detectadas[idx] if idx < len(respuestas_detectadas) else "N/A"
                
                respuestas_alumno_json[prog] = marcada
                
                if marcada == correcta:
                    estado_icono = "✅"
                    aciertos += 1
                    puntaje_final += peso
                elif marcada == "BLANCO":
                    estado_icono = "⚪ (Vacía)"
                else:
                    estado_icono = "❌"
                
                tabla_comparativa.append({
                    "Ítem": prog.replace("Pregunta ", "P"),
                    "Detección de IA": marcada,
                    "Clave del Profesor": correcta,
                    "Veredicto": estado_icono
                })
            
            df_tabla = pd.DataFrame(tabla_comparativa)
            st.dataframe(df_tabla.set_index("Ítem").T, use_container_width=True)

            porcentaje_efectividad = (aciertos / total_preguntas) * 100 if total_preguntas > 0 else 0

            st.markdown("#### 📊 Calificación Final (Automática)")
            c_m1, c_m2, c_m3 = st.columns(3)
            with c_m1: st.metric("🎯 Aciertos Netos", f"{aciertos} / {total_preguntas}")
            with c_m2: st.metric("🎖️ Nota Definitiva", f"{puntaje_final:.2f} / {datos_prueba['puntaje_maximo']:.1f}")
            with c_m3: st.metric("📈 Porcentaje", f"{porcentaje_efectividad:.1f}%")

            if st.button("💾 CONFIRMAR Y SUBIR NOTA A LA BASE DE DATOS", use_container_width=True, type="primary"):
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
                    st.success(f"🎉 ¡Misión cumplida! La calificación de '{nombre_identificado}' ya está segura en el Búnker Analítico.")
                    st.balloons()
                except Exception as e:
                    st.error(f"Falla al registrar la calificación: {e}")

        except Exception as e_critico:
            st.error(f"🚨 **RADAR DE FALLOS:** {e_critico}")

if __name__ == "__main__":
    ejecutar()
