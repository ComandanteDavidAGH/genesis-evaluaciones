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
    # Cabecera de la Plataforma Forzada con Estilos Directos
    st.markdown("<h1 style='color: #0d1b2a; font-family: \"Arial Black\", sans-serif; font-size: 32px; margin-bottom: 0px;'>⚙️ Creador de Plantillas Maestras</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #d4af37; font-weight: bold; font-size: 14px; margin-top: -5px; letter-spacing: 1px; text-transform: uppercase;'>Módulo de Configuración Óptica Avanzada</p>", unsafe_allow_html=True)
    st.markdown("---")

    try:
        supabase = iniciar_conexion()
    except Exception as e:
        st.error(f"🚨 Error de conexión con la base de datos: {e}")
        return

    # 🏢 Formulario de Datos Básicos dentro de la Tarjeta con Estilo Directo
    st.markdown("""
        <div style="background-color: #f8f9fa; border-left: 5px solid #0d1b2a; padding: 20px; border-radius: 4px 12px 12px 4px; box-shadow: 0 4px 6px rgba(0,0,0,0.03); margin-bottom: 15px;">
            <h4 style="color: #0d1b2a; font-weight: bold; margin-top: 0px; margin-bottom: 15px;">📝 Datos Generals del Examen</h4>
        </div>
    """, unsafe_allow_html=True)
    
    # Render de los inputs normales de Streamlit
    c1, c2 = st.columns(2)
    with c1:
        nombre_examen = st.text_input("🎯 Nombre de la Evaluación:", placeholder="Ej: Bimestral Primer Periodo")
        listado_materias = [
            "--- Seleccione una Asignatura ---", "Matemáticas", "Lengua Castellana / Lenguaje",
            "Ciencias Naturales / Biología", "Ciencias Sociales / Historia", "Inglés",
            "Física", "Química", "Filosofía", "Tecnología e Informática",
            "Educación Física", "Educación Artística", "Ética y Valores", "Religión"
        ]
        materia = st.selectbox("📚 Asignatura / Materia:", listado_materias)
        
    with c2:
        total_preguntas = st.number_input("🔢 Número de Ítems / Preguntas:", min_value=1, max_value=100, value=10, step=1)
        puntaje_maximo = st.number_input("🎖️ Nota Máxima Posible (Escala del Colegio):", min_value=1.0, max_value=100.0, value=5.0, step=0.1)

    # Cálculo dinámico para las casillas
    peso_por_pregunta = puntaje_maximo / total_preguntas if total_preguntas > 0 else 0

    # =================================================================
    # 🎛️ CASILLAS DE TELEMETRÍA FORZADAS POR INLINE STYLES (IMPOSIBLE DE IGNORAR)
    # =================================================================
    st.markdown("<br><h3 style='color: #0d1b2a; margin-bottom: 15px; font-weight: bold;'>📊 Resumen de Configuración</h3>", unsafe_allow_html=True)
    
    col_card1, col_card2, col_card3 = st.columns(3)
    
    # Tarjeta 1: Total Preguntas
    with col_card1:
        st.markdown(f"""
            <div style="background-color: #ffffff; border-radius: 12px; padding: 15px 10px; text-align: center; box-shadow: 0 6px 15px rgba(0, 0, 0, 0.08); border: 2.5px solid #0d1b2a; margin-bottom: 15px;">
                <div style="font-size: 11px; font-weight: 800; text-transform: uppercase; letter-spacing: 1px; color: #0d1b2a; margin-bottom: 5px;">🔢 TOTAL PREGUNTAS</div>
                <div style="font-size: 36px; font-family: 'Arial Black', sans-serif; font-weight: 900; line-height: 1; color: #0d1b2a; margin: 0;">{total_preguntas}</div>
            </div>
        """, unsafe_allow_html=True)
        
    # Tarjeta 2: Valor por Acierto
    with col_card2:
        st.markdown(f"""
            <div style="background-color: #ffffff; border-radius: 12px; padding: 15px 10px; text-align: center; box-shadow: 0 6px 15px rgba(0, 0, 0, 0.08); border: 2.5px solid #d4af37; margin-bottom: 15px;">
                <div style="font-size: 11px; font-weight: 800; text-transform: uppercase; letter-spacing: 1px; color: #bfa12a; margin-bottom: 5px;">🎯 VALOR POR ACERTO</div>
                <div style="font-size: 36px; font-family: 'Arial Black', sans-serif; font-weight: 900; line-height: 1; color: #d4af37; margin: 0;">{peso_por_pregunta:.2f}</div>
            </div>
        """, unsafe_allow_html=True)
        
    # Tarjeta 3: Nota Máxima
    with col_card3:
        st.markdown(f"""
            <div style="background-color: #ffffff; border-radius: 12px; padding: 15px 10px; text-align: center; box-shadow: 0 6px 15px rgba(0, 0, 0, 0.08); border: 2.5px solid #2b9348; margin-bottom: 15px;">
                <div style="font-size: 11px; font-weight: 800; text-transform: uppercase; letter-spacing: 1px; color: #2b9348; margin-bottom: 5px;">🎖️ NOTA MÁXIMA</div>
                <div style="font-size: 36px; font-family: 'Arial Black', sans-serif; font-weight: 900; line-height: 1; color: #2b9348; margin: 0;">{puntaje_maximo:.1f}</div>
            </div>
        """, unsafe_allow_html=True)

    # 🎯 REJILLA DE RESPUESTAS CON ENCABEZADOS FORZADOS
    st.markdown("<br><h3 style='color: #0d1b2a; font-weight: bold;'>🎛️ Matriz de la Llave Maestra</h3>", unsafe_allow_html=True)
    
    style_th = "color: #0d1b2a; font-weight: bold; font-size: 13px; text-transform: uppercase; letter-spacing: 0.5px; border-bottom: 2px solid #d4af37; padding-bottom: 5px; margin-bottom: 15px;"
    
    c_head1, c_head2, c_head3 = st.columns([1, 2, 4])
    with c_head1:
        st.markdown(f"<div style='{style_th}'>🔢 Ítems</div>", unsafe_allow_html=True)
    with c_head2:
        st.markdown(f"<div style='{style_th}'>🔑 Clave de Respuesta</div>", unsafe_allow_html=True)
    with c_head3:
        st.markdown(f"<div style='{style_th}'>🏷️ Tema o Competencia Evaluada</div>", unsafe_allow_html=True)

    # Generación dinámica de la matriz de respuestas
    opciones_abc = ["A", "B", "C", "D", "E"]
    llave_maestra_lista = []

    for i in range(total_preguntas):
        fila_preg, fila_resp, fila_tema = st.columns([1, 2, 4])
        
        with fila_preg:
            st.markdown(f"<div style='padding-top: 5px; font-weight: bold; color: #0d1b2a;'>Ítem N° {i+1}</div>", unsafe_allow_html=True)
            
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
    
    # 💾 Botón de registro oficial
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
