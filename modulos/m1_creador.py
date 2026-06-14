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
    # 🎨 INYECCIÓN ESTÉTICA SEGURA (Contornos Dorados)
    st.markdown("""
        <style>
        .titulo-genesis {
            color: #0d1b2a;
            font-family: 'Arial Black', sans-serif;
            font-size: 32px;
            margin-bottom: 0px;
        }
        .subtitulo-genesis {
            color: #d4af37;
            font-weight: bold;
            font-size: 14px;
            margin-top: -5px;
            letter-spacing: 1px;
            text-transform: uppercase;
        }
        
        /* HACK DE CONTORNOS ESPECIALES (Estilo Génesis Omega) */
        div[data-baseweb="input"] {
            border: 2px solid #d4af37 !important;
            border-radius: 8px !important;
            background-color: #ffffff !important;
            transition: all 0.2s ease-in-out !important;
        }
        div[data-baseweb="select"] {
            border: 2px solid #d4af37 !important;
            border-radius: 8px !important;
            background-color: #ffffff !important;
            transition: all 0.2s ease-in-out !important;
        }
        
        div[data-baseweb="input"]:focus-within {
            border-color: #0d1b2a !important;
            box-shadow: 0 0 8px rgba(13, 27, 42, 0.2) !important;
        }
        div[data-baseweb="select"]:focus-within {
            border-color: #0d1b2a !important;
            box-shadow: 0 0 8px rgba(13, 27, 42, 0.2) !important;
        }

        .casilla-telemetria {
            background-color: #ffffff;
            border-radius: 12px;
            padding: 15px 10px;
            text-align: center;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.04);
            margin-bottom: 15px;
        }
        
        .encabezado-tabla {
            color: #0d1b2a;
            font-weight: bold;
            font-size: 13px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            border-bottom: 2px solid #0d1b2a;
            padding-bottom: 5px;
            margin-bottom: 15px;
        }
        </style>
    """, unsafe_allow_html=True)

    # Cabecera oficial con Faro de Control integrado
    st.markdown("<p class='titulo-genesis'>⚙️ Creador de Plantillas Maestras</p>", unsafe_allow_html=True)
    st.markdown("<p class='subtitulo-genesis'>Módulo de Configuración Óptica Avanzada v2.5</p>", unsafe_allow_html=True)
    st.markdown("---")

    try:
        supabase = iniciar_conexion()
    except Exception as e:
        st.error(f"🚨 Error de conexión con la base de datos: {e}")
        return

    # 🏢 Formulario Seguro Usando Contenedores Nativos de Streamlit
    st.markdown("<h4 style='color: #0d1b2a; font-weight: bold; margin-bottom: 10px;'>📝 Datos Generales del Examen</h4>", unsafe_allow_html=True)
    
    with st.container(border=True):
        # 📡 FILA 1: Parametrización y Clasificación (3 Columnas Equilibradas)
        fila1_c1, fila1_c2, fila1_c3 = st.columns(3)
        with fila1_c1:
            nombre_examen = st.text_input("🎯 Nombre de la Evaluación:", placeholder="Ej: Bimestral Primer Periodo")
        with fila1_c2:
            listado_materias = [
                "--- Seleccione una Asignatura ---", "Matemáticas", "Lengua Castellana / Lenguaje",
                "Ciencias Naturales / Biología", "Ciencias Sociales / Historia", "Inglés",
                "Física", "Química", "Filosofía", "Tecnología e Informática",
                "Educación Física", "Educación Artística", "Ética y Valores", "Religión"
            ]
            materia = st.selectbox("📚 Asignatura / Materia:", listado_materias)
        with fila1_c3:
            listado_tipos = [
                "--- Seleccione Tipo de Evaluación ---",
                "Quiz",
                "Evaluación Primer Periodo",
                "Evaluación Segundo Periodo",
                "Evaluación Tercer Periodo",
                "Evaluación Cuarto Periodo",
                "Prepruebas Saber Pro"
            ]
            tipo_evaluacion = st.selectbox("📋 Tipo de Evaluación:", listado_tipos)
            
        # 📡 FILA 2: Segmentación y Telemetría Escolar (3 Columnas)
        fila2_c1, fila2_c2, fila2_c3 = st.columns(3)
        with fila2_c1:
            listado_grados = [
                "--- Seleccione un Grado ---", 
                "1°", "2°", "3°", "4°", "5°", "6°", "7°", "8°", "9°", "10°", "11°"
            ]
            grado = st.selectbox("🏫 Grado / Curso Destino:", listado_grados)
        with fila2_c2:
            total_preguntas = st.number_input("🔢 Número de Ítems / Preguntas:", min_value=1, max_value=100, value=10, step=1)
        with fila2_c3:
            puntaje_maximo = st.number_input("🎖️ Nota Máxima Posible (Escala del Colegio):", min_value=1.0, max_value=100.0, value=5.0, step=0.1)

    # Cálculos dinámicos
    peso_por_pregunta = puntaje_maximo / total_preguntas if total_preguntas > 0 else 0

    # 📊 Cuadros de Mando Interactivos
    st.markdown("<br><h3 style='color: #0d1b2a; margin-bottom: 15px; font-weight: bold;'>📊 Resumen de Configuración</h3>", unsafe_allow_html=True)
    col_card1, col_card2, col_card3 = st.columns(3)
    
    with col_card1:
        st.markdown(f'<div class="casilla-telemetria" style="border: 2px solid #0d1b2a;"><div style="font-size: 11px; font-weight: 800; color: #0d1b2a; margin-bottom: 5px;">🔢 TOTAL PREGUNTAS</div><div style="font-size: 32px; font-family: \'Arial Black\', sans-serif; font-weight: 900; color: #0d1b2a;">{total_preguntas}</div></div>', unsafe_allow_html=True)
        
    with col_card2:
        st.markdown(f'<div class="casilla-telemetria" style="border: 2px solid #d4af37;"><div style="font-size: 11px; font-weight: 800; color: #bfa12a; margin-bottom: 5px;">🎯 VALOR POR ACERTO</div><div style="font-size: 32px; font-family: \'Arial Black\', sans-serif; font-weight: 900; color: #d4af37;">{peso_por_pregunta:.2f}</div></div>', unsafe_allow_html=True)
        
    with col_card3:
        st.markdown(f'<div class="casilla-telemetria" style="border: 2px solid #2b9348;"><div style="font-size: 11px; font-weight: 800; color: #2b9348; margin-bottom: 5px;">🎖️ NOTA MÁXIMA</div><div style="font-size: 32px; font-family: \'Arial Black\', sans-serif; font-weight: 900; color: #2b9348;">{puntaje_maximo:.1f}</div></div>', unsafe_allow_html=True)

    # 🎛️ La Rejilla de Configuración Inferior
    st.markdown("<br><h3 style='color: #0d1b2a; font-weight: bold;'>🎛️ Matriz de la Llave Maestra</h3>", unsafe_allow_html=True)
    
    c_head1, c_head2, c_head3 = st.columns([1, 2, 4])
    with c_head1:
        st.markdown("<div class='encabezado-tabla'>🔢 Ítems</div>", unsafe_allow_html=True)
    with c_head2:
        st.markdown("<div class='encabezado-tabla'>🔑 Clave de Respuesta</div>", unsafe_allow_html=True)
    with c_head3:
        st.markdown("<div class='encabezado-tabla'>🏷️ Tema o Competencia Evaluada</div>", unsafe_allow_html=True)

    opciones_abc = ["A", "B", "C", "D", "E"]
    llave_maestra_lista = []

    for i in range(total_preguntas):
        fila_preg, fila_resp, fila_tema = st.columns([1, 2, 4])
        
        with fila_preg:
            st.markdown(f"<div style='padding-top: 5px; font-weight: bold; color: #0d1b2a;'>Ítem N° {i+1}</div>", unsafe_allow_html=True)
            
        with fila_resp:
            opcion_correcta = st.selectbox(f"Resp_{i}", opciones_abc, key=f"resp_{i}", label_visibility="collapsed")
            
        with fila_tema:
            tema_pedagogico = st.text_input(f"Tema_{i}", value="Conceptos Clave", key=f"tema_{i}", label_visibility="collapsed")
            
        llave_maestra_lista.append({
            "Pregunta": f"Pregunta {i+1}",
            "Respuesta Correcta": opcion_correcta,
            "Puntaje (Peso)": round(peso_por_pregunta, 2),
            "Tema/Competencia": tema_pedagogico.strip()
        })

    st.markdown("---")
    
    if st.button("💾 GUARDAR CONFIGURACIÓN Y CREAR PLANTILLA", use_container_width=True, type="primary"):
        if not nombre_examen.strip():
            st.error("❌ Por favor, asigne un nombre a la evaluación antes de guardar.")
            return
            
        if materia == "--- Seleccione una Asignatura ---":
            st.error("❌ Por favor, seleccione una asignatura válida del menú desplegable.")
            return
            
        if tipo_evaluacion == "--- Seleccione Tipo de Evaluación ---":
            st.error("❌ Por favor, especifique el tipo de evaluación para el cálculo de ponderaciones.")
            return
            
        if grado == "--- Seleccione un Grado ---":
            st.error("❌ Por favor, especifique el grado al que va dirigida esta evaluación.")
            return

        paquete_datos = {
            "nombre": nombre_examen.strip(),
            "materia": materia,
            "tipo_evaluacion": tipo_evaluacion,
            "grado": grado,
            "total_preguntas": total_preguntas,
            "puntaje_maximo": puntaje_maximo,
            "llave_maestra": llave_maestra_lista
        }

        with st.spinner("Subiendo plantilla de evaluación al servidor central..."):
            try:
                supabase.table("pruebas_maestras").insert(paquete_datos).execute()
                st.success(f"🎉 ¡Éxito absoluto! La evaluación '{nombre_examen}' ({tipo_evaluacion}) ha sido guardada para el grado {grado}.")
                st.balloons()
            except Exception as error:
                st.error(f"🚨 Error al guardar en la base de datos: {error}")
