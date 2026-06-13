import streamlit as st
import json
from supabase import create_client, Client

# =================================================================
# 🔒 CONEXIÓN SEGURA CON EL BÚNKER DE PRODUCCIÓN
# =================================================================
def iniciar_conexion():
    url = st.secrets["SUPABASE_URL"].strip()
    key = st.secrets["SUPABASE_KEY"].strip()
    return create_client(url, key)

def ejecutar():
    st.markdown("<h1 style='color: #0d1b2a;'>⚙️ Creador de Plantillas Maestras</h1>", unsafe_allow_html=True)
    st.caption("Diseñe la estructura de respuestas y componentes pedagógicos para la lectura óptica.")
    st.markdown("---")

    try:
        supabase = iniciar_conexion()
    except Exception as e:
        st.error(f"🚨 Error de conexión con la base de datos: {e}")
        return

    # 🏢 Formulario de Datos Básicos de la Evaluación
    with st.container(border=True):
        st.markdown("#### 📝 Datos Generales del Examen")
        c1, c2 = st.columns(2)
        with c1:
            nombre_examen = st.text_input("🎯 Nombre de la Evaluación:", placeholder="Ej: Bimestral Primer Periodo")
            
            # 📦 LISTADO OFICIAL DE MATERIAS INSTITUCIONALES
            listado_materias = [
                "--- Seleccione una Asignatura ---",
                "Matemáticas",
                "Lengua Castellana / Lenguaje",
                "Ciencias Naturales / Biología",
                "Ciencias Sociales / Historia",
                "Inglés",
                "Física",
                "Química",
                "Filosofía",
                "Tecnología e Informática",
                "Educación Física",
                "Educación Artística",
                "Ética y Valores",
                "Religión"
            ]
            materia = st.selectbox("📚 Asignatura / Materia:", listado_materias)
            
        with c2:
            total_preguntas = st.number_input("🔢 Número de Ítems / Preguntas:", min_value=1, max_value=100, value=10, step=1)
            puntaje_maximo = st.number_input("🎖️ Nota Máxima Posible (Escala del Colegio):", min_value=1.0, max_value=100.0, value=5.0, step=0.1)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### 🎛️ Configuración de la Llave Maestra y Temas Diagnósticos")
    
    peso_por_pregunta = puntaje_maximo / total_preguntas if total_preguntas > 0 else 0
    st.info(f"💡 **Información para el Docente:** Cada acierto aportará automáticamente **{peso_por_pregunta:.2f} puntos** a la nota definitiva.")

    # 🎯 LA FIJACIÓN DE TÍTULOS MAESTROS
    st.markdown("<br>", unsafe_allow_html=True)
    c_head1, c_head2, c_head3 = st.columns([1, 2, 4])
    with c_head1:
        st.markdown("<p style='color: #0d1b2a; font-weight: bold; margin-bottom: 0;'>🔢 Pregunta</p>", unsafe_allow_html=True)
    with c_head2:
        st.markdown("<p style='color: #0d1b2a; font-weight: bold; margin-bottom: 0;'>🔑 Respuesta Correcta</p>", unsafe_allow_html=True)
    with c_head3:
        st.markdown("<p style='color: #0d1b2a; font-weight: bold; margin-bottom: 0;'>🏷️ Tema, Competencia o Componente Evaluado</p>", unsafe_allow_html=True)
    st.markdown("<hr style='margin-top: 5px; margin-bottom: 15px;'>", unsafe_allow_html=True)

    # Generación dinámica de la matriz de respuestas
    opciones_abc = ["A", "B", "C", "D", "E"]
    llave_maestra_lista = []

    for i in range(total_preguntas):
        fila_preg, fila_resp, fila_tema = st.columns([1, 2, 4])
        
        with fila_preg:
            st.markdown(f"<div style='padding-top: 5px; font-weight: bold; color: #555;'>Ítem N° {i+1}</div>", unsafe_allow_html=True)
            
        with fila_resp:
            opcion_correcta = st.selectbox(
                f"Resp_{i}", opciones_abc, key=f"resp_{i}", 
                label_visibility="collapsed"
            )
            
        with fila_tema:
            tema_pedagogico = st.text_input(
                f"Tema_{i}", value="Conceptos Clave", key=f"tema_{i}", 
                placeholder="Ej: Comprensión Lectora, Álgebra, etc.",
                label_visibility="collapsed"
            )
            
        llave_maestra_lista.append({
            "Pregunta": f"Pregunta {i+1}",
            "Respuesta Correcta": opcion_correcta,
            "Puntaje (Peso)": round(peso_por_pregunta, 2),
            "Tema/Competencia": tema_pedagogico.strip()
        })

    st.markdown("---")
    
    # 💾 Botón de registro oficial en Supabase
    if st.button("💾 GUARDAR CONFIGURACIÓN Y CREAR PLANTILLA", use_container_width=True, type="primary"):
        if not nombre_examen.strip():
            st.error("❌ Por favor, asigne un nombre a la evaluación antes de guardar.")
            return
            
        if materia == "--- Seleccione una Asignatura ---":
            st.error("❌ Por favor, seleccione una asignatura válida del menú desplegable.")
            return

        paquete_datos = {
            "nombre": nombre_examen.strip(),
            "materia": materia,
            "total_preguntas": total_preguntas,
            "puntaje_maximo": puntaje_maximo,
            "llave_maestra": llave_maestra_lista
        }

        with st.spinner("Subiendo plantilla de evaluación al servidor central..."):
            try:
                supabase.table("pruebas_maestras").insert(paquete_datos).execute()
                st.success(f"🎉 ¡Éxito absoluto! La evaluación '{nombre_examen}' ha sido guardada para la materia de {materia}.")
                st.balloons()
            except Exception as error:
                st.error(f"🚨 Error al guardar en la base de datos institucional: {error}")
