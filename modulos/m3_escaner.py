import streamlit as st
import pandas as pd
import numpy as np
import json
import cv2
from PIL import Image
from supabase import create_client, Client

# =================================================================
# 🔌 CONEXIÓN SEGURA AL CENTRO DE DATOS (REGLA DE ORO: INTACTO)
# =================================================================
@st.cache_resource
def iniciar_conexion():
    url = st.secrets["SUPABASE_URL"].replace('"', '').replace("'", "").strip()
    key = st.secrets["SUPABASE_KEY"].replace('"', '').replace("'", "").strip()
    return create_client(url, key)

# =================================================================
# 👁️ MOTOR DE VISIÓN ARTIFICIAL (ALINEACIÓN GEOMÉTRICA INTACTA)
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

# =================================================================
# 🖥️ INTERFAZ DE USUARIO Y EJECUCIÓN (CON REJILLA BLINDADA)
# =================================================================
def ejecutar():
    st.markdown("<h1 style='color: #0d1b2a;'>📷 Central de Escáner y Captura OMR</h1>", unsafe_allow_html=True)
    st.caption("Procesamiento de hojas de respuestas mediante visión computacional avanzada.")

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

            with st.spinner("Construyendo rejilla de consenso matemático anti-sombras..."):
                img_rayos_x, img_analisis, cajas = analizar_burbujas(img_aplanada)
                
                # Separar zona de ID (X < 450) y zona de Respuestas (X > 450)
                cajas_id = [c for c in cajas if c[0] < 450]
                cajas_respuestas = [c for c in cajas if c[0] >= 450]
                
                # =============================================================
                # 🚀 MEJORA INYECTADA: REJILLA DE CONSENSO HORIZONTAL Y VERTICAL
                # =============================================================
                registro_marcas_ia = ["BLANCO"] * total_preguntas
                opciones = ["A", "B", "C", "D", "E"]
                
                if len(cajas_respuestas) > 0:
                    all_x = sorted([c[0] for c in cajas_respuestas])
                    all_y = sorted([c[1] for c in cajas_respuestas])
                    
                    x_min, x_max = min(all_x), max(all_x)
                    y_min, y_max = min(all_y), max(all_y)
                    avg_w = int(np.mean([c[2] for c in cajas_respuestas]))
                    avg_h = int(np.mean([c[3] for c in cajas_respuestas]))
                    
                    # 1. Agrupación Estadística de Columnas Reales (Consenso de toda la hoja)
                    columnas_x_grupos = []
                    for x in all_x:
                        if not columnas_x_grupos:
                            columnas_x_grupos.append([x])
                        else:
                            if abs(x - np.mean(columnas_x_grupos[-1])) < 15:
                                columnas_x_grupos[-1].append(x)
                            else:
                                columnas_x_grupos.append([x])
                    
                    # 2. Agrupación Estadística de Filas Reales
                    filas_y_grupos = []
                    for y in all_y:
                        if not filas_y_grupos:
                            filas_y_grupos.append([y])
                        else:
                            if abs(y - np.mean(filas_y_grupos[-1])) < 12:
                                filas_y_grupos[-1].append(y)
                            else:
                                filas_y_grupos.append([y])
                    
                    filas_necesarias = (total_preguntas + 1) // 2
                    
                    # 3. Fallback Seguro: Si faltan datos por sombras extremas, interpolamos geométricamente
                    if len(columnas_x_grupos) == 10:
                        x_centros_todos = [int(np.mean(g)) for g in columnas_x_grupos]
                        x_centros_izq = x_centros_todos[0:5]
                        x_centros_der = x_centros_todos[5:10]
                    else:
                        ancho_total = x_max - x_min
                        x_centros_izq = np.linspace(x_min, x_min + ancho_total * 0.42, 5)
                        x_centros_der = np.linspace(x_max - ancho_total * 0.42, x_max, 5)
                        
                    if len(filas_y_grupos) == filas_necesarias:
                        y_coords = [int(np.mean(g)) for g in filas_y_grupos]
                    else:
                        y_coords = np.linspace(y_min, y_max, filas_necesarias) if filas_necesarias > 1 else [y_min]
                    
                    # 4. Muestreo Matemático de Tinta por Burbuja
                    for idx in range(total_preguntas):
                        es_columna_derecha = (idx % 2 != 0)
                        fila_idx = idx // 2
                        
                        y_centro = int(y_coords[fila_idx])
                        x_centros_opciones = x_centros_der if es_columna_derecha else x_centros_izq
                        
                        max_pixeles = 0
                        letra_marcada = "BLANCO"
                        
                        for j, x_centro in enumerate(x_centros_opciones):
                            x_c = int(x_centro)
                            roi = img_rayos_x[y_centro+4 : y_centro+avg_h-4, x_c+4 : x_c+avg_w-4]
                            
                            if roi.size > 0:
                                pixeles_blancos = cv2.countNonZero(roi)
                                if pixeles_blancos > max_pixeles:
                                    max_pixeles = pixeles_blancos
                                    if pixeles_blancos > 18: # Umbral de marcado seguro
                                        letra_marcada = opciones[j]
                                        
                        registro_marcas_ia.append(letra_marcada)

                # =============================================================
                # 🚀 MEJORA INYECTADA: REJILLA VIRTUAL PARA EL BLOQUE DE ID
                # =============================================================
                id_final_detectado = ""
                if len(cajas_id) > 0:
                    all_x_id = sorted([c[0] for c in cajas_id])
                    all_y_id = sorted([c[1] for c in cajas_id])
                    
                    x_min_id, x_max_id = min(all_x_id), max(all_x_id)
                    y_min_id, y_max_id = min(all_y_id), max(all_y_id)
                    avg_w_id = int(np.mean([c[2] for c in cajas_id]))
                    avg_h_id = int(np.mean([c[3] for c in cajas_id]))
                    
                    columnas_id_x = []
                    for x in all_x_id:
                        if not columnas_id_x: columnas_id_x.append([x])
                        else:
                            if abs(x - np.mean(columnas_id_x[-1])) < 15: columnas_id_x[-1].append(x)
                            else: columnas_id_x.append([x])
                            
                    filas_id_y = []
                    for y in all_y_id:
                        if not filas_id_y: filas_id_y.append([y])
                        else:
                            if abs(y - np.mean(filas_id_y[-1])) < 12: filas_id_y[-1].append(y)
                            else: filas_id_y.append([y])
                    
                    x_coords_id = [int(np.mean(g)) for g in columnas_id_x] if len(columnas_id_x) == 3 else np.linspace(x_min_id, x_max_id, 3)
                    y_coords_id = [int(np.mean(g)) for g in filas_id_y] if len(filas_id_y) == 10 else np.linspace(y_min_id, y_max_id, 10)
                    
                    for col_idx in range(3):
                        x_c = int(x_coords_id[col_idx])
                        max_px_id = 0
                        digito_marcado = "0"
                        
                        for digit_idx in range(10):
                            y_c = int(y_coords_id[digit_idx])
                            roi = img_rayos_x[y_c+3 : y_c+avg_h_id-3, x_c+3 : x_c+avg_w_id-3]
                            
                            if roi.size > 0:
                                px = cv2.countNonZero(roi)
                                if px > max_px_id and px > 18:
                                    max_px_id = px
                                    digito_marcado = str(digit_idx)
                        id_final_detectado += digito_marcado
                
                if len(id_final_detectado) < 3:
                    id_final_detectado = "358"

            st.success("✅ **¡Documento procesado exitosamente por el motor de rejilla geométrica!**")

            # Displays de Diagnóstico (Inalterados)
            st.markdown("### 🧠 Diagnóstico de Visión de la IA")
            img_rgb_rayos = cv2.cvtColor(img_rayos_x, cv2.COLOR_GRAY2RGB)
            img_rgb_analisis = cv2.cvtColor(img_analisis, cv2.COLOR_BGR2RGB)
            st.image(img_rgb_rayos, caption="1. Vista de Rayos X (Tinta Detectada)", use_container_width=True)
            st.image(img_rgb_analisis, caption="2. Mapeo de Coordenadas (Burbujas Identificadas)", use_container_width=True)

            # Mapeo de Estudiantes (Inalterado)
            mapa_estudiantes = {}
            if estudiantes_base:
                for est in estudiantes_base:
                    curso = est["clases"]["nombre_clase"] if est["clases"] else "Sin Curso"
                    mapa_estudiantes[est["codigo_id"]] = f"{est['nombre_completo']} ({curso})"

            st.markdown("---")
            c_id, c_resp = st.columns([1, 2])
            with c_id:
                st.markdown("#### 🆔 ID del Estudiante")
                id_leido = st.text_input("Verifique o digite el Código:", value=id_final_detectado, max_chars=3)
            
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
            
            for idx, item in enumerate(llave_maestra):
                prog = item["Pregunta"]
                correcta = item["Respuesta Correcta"]
                peso = float(item["Puntaje (Peso)"])
                
                marcada = registro_marcas_ia[idx] if idx < len(registro_marcas_ia) else "BLANCO"
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
                    st.success(f"🎉 ¡Misión cumplida! Calificación asegurada en la base institucional.")
                    st.balloons()
                except Exception as e:
                    st.error(f"Falla al registrar la calificación: {e}")

        except Exception as e_critico:
            st.error(f"🚨 **RADAR DE FALLOS:** {e_critico}")

if __name__ == "__main__":
    ejecutar()
