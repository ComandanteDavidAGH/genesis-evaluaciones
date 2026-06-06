import streamlit as st
from supabase import create_client, Client
import json

# =================================================================
# 🔌 CONEXIÓN AL BÚNKER
# =================================================================
@st.cache_resource
def iniciar_conexion():
    url = st.secrets["SUPABASE_URL"].replace('"', '').replace("'", "").strip()
    key = st.secrets["SUPABASE_KEY"].replace('"', '').replace("'", "").strip()
    return create_client(url, key)
def ejecutar():
    st.markdown("""
    <style>
    .titulo-estudiante { color: #0d1b2a; border-bottom: 3px solid #d4af37; padding-bottom: 5px; font-family: 'Arial Black'; }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("<h1 class='titulo-estudiante'>📱 Portal de Evaluación Estudiantil</h1>", unsafe_allow_html=True)

    try:
        supabase: Client = iniciar_conexion()
    except Exception:
        st.error("⚠️ Error de conexión. Llama al docente.")
        return

    # 1. Extraer las pruebas disponibles de la Base de Datos
    try:
        respuesta = supabase.table("pruebas_maestras").select("*").execute()
        pruebas = respuesta.data
    except Exception as e:
        st.error(f"Error al descargar las pruebas: {e}")
        return

    if not pruebas:
        st.info("📭 No hay simulacros activos en este momento.")
        return

    # 2. Interfaz de Selección
    opciones_pruebas = {f"{p['nombre']} - {p['materia']}": p for p in pruebas}
    prueba_seleccionada = st.selectbox("📚 Selecciona la prueba a presentar:", ["--- Selecciona ---"] + list(opciones_pruebas.keys()))

    if prueba_seleccionada != "--- Selecciona ---":
        datos_prueba = opciones_pruebas[prueba_seleccionada]
        llave = datos_prueba["llave_maestra"]

        with st.container(border=True):
            st.markdown("### 👤 Datos del Estudiante")
            estudiante = st.text_input("Escribe tu Nombre Completo y Grado (Ej: Juan Pérez - 10A)")

        if estudiante:
            st.markdown("---")
            st.markdown(f"### 📝 Simulacro: {datos_prueba['nombre']}")
            
            respuestas_estudiante = {}
            
            # 3. Construir el Cuestionario Dinámico
            with st.form("form_examen"):
                for item in llave:
                    pregunta = item["Pregunta"]
                    # Deducir opciones basándonos en la respuesta correcta (V/F o A/B/C/D)
                    if item["Respuesta Correcta"] in ["V", "F"]: opciones = ["V", "F"]
                    elif item["Respuesta Correcta"] == "E": opciones = ["A", "B", "C", "D", "E"]
                    else: opciones = ["A", "B", "C", "D"]

                    respuestas_estudiante[pregunta] = st.radio(pregunta, opciones, horizontal=True)

                st.markdown("---")
                submit = st.form_submit_button("✅ Finalizar y Calificar", type="primary", use_container_width=True)

            # 4. Motor de Calificación Automática
            if submit:
                with st.spinner("Calificando respuestas con IA..."):
                    puntaje_total = 0.0
                    maximo_posible = float(datos_prueba["puntaje_maximo"])

                    for item in llave:
                        pregunta = item["Pregunta"]
                        peso = float(item["Puntaje (Peso)"])
                        if respuestas_estudiante[pregunta] == item["Respuesta Correcta"]:
                            puntaje_total += peso

                    porcentaje = (puntaje_total / maximo_posible) * 100 if maximo_posible > 0 else 0

                    # 5. Guardar nota en la Base de Datos
                    paquete_nota = {
                        "id_prueba": datos_prueba["id_prueba"],
                        "nombre_prueba": datos_prueba["nombre"],
                        "estudiante": estudiante.strip(),
                        "puntaje_obtenido": puntaje_total,
                        "puntaje_maximo": maximo_posible,
                        "porcentaje": round(porcentaje, 2),
                        "respuestas_json": respuestas_estudiante
                    }
                    try:
                        supabase.table("respuestas_estudiantes").insert(paquete_nota).execute()
                        st.balloons()
                        st.success("🎉 ¡Prueba entregada y guardada con éxito!")
                        
                        # Mostrar HUD de Resultados
                        c1, c2, c3 = st.columns(3)
                        c1.metric("Aciertos (Puntos)", f"{puntaje_total} / {maximo_posible}")
                        c2.metric("Efectividad", f"{porcentaje:.1f}%")
                        
                        if porcentaje >= 60: c3.success("ESTADO: APROBADO ✅")
                        else: c3.error("ESTADO: REPROBADO ❌")
                    except Exception as e:
                        st.error(f"💥 Error al guardar la calificación: {e}")
