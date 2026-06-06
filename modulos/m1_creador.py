import streamlit as st
import pandas as pd
from datetime import datetime
from supabase import create_client, Client

# =================================================================
# 🔌 CONEXIÓN AL BÚNKER (SUPABASE)
# =================================================================
@st.cache_resource
def iniciar_conexion():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

try:
    supabase: Client = iniciar_conexion()
except Exception as e:
    st.error("⚠️ Falla en la conexión al Búnker. Verifique las llaves en los Secrets de Streamlit.")

def ejecutar():
    # =================================================================
    # 🎨 ESTILOS Y UX (UI/UX)
    # =================================================================
    st.markdown("""
    <style>
    .titulo-modulo { color: #0d1b2a; border-bottom: 3px solid #d4af37; padding-bottom: 5px; font-family: 'Arial Black'; }
    .stAlert { border-radius: 8px; border-left: 4px solid #d4af37; }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("<h1 class='titulo-modulo'>⚙️ Centro de Comando: Configuración de Pruebas</h1>", unsafe_allow_html=True)
    st.info("💡 Diseñe el simulacro, establezca la Llave Maestra de respuestas y transmítalo a la Base de Datos.")

    # =================================================================
    # 📝 SECCIÓN 1: METADATOS DEL SIMULACRO
    # =================================================================
    with st.container(border=True):
        st.markdown("### 📋 Detalles del Cuestionario")
        
        c1, c2, c3 = st.columns(3)
        nombre_prueba = c1.text_input("📝 Nombre de la Prueba", placeholder="Ej: Ciencias Sociales - Grado 10")
        materia = c2.selectbox("📚 Materia / Área", ["Ciencias Sociales", "Matemáticas", "Lectura Crítica", "Ciencias Naturales", "Inglés", "Otra"])
        fecha_prueba = c3.date_input("📅 Fecha Programada", datetime.today())

        c4, c5 = st.columns([1, 2])
        num_preguntas = c4.number_input("🔢 Número de Preguntas", min_value=1, max_value=100, value=20, step=1)
        tipo_opciones = c5.selectbox("🔠 Formato de Opciones", ["A, B, C, D", "A, B, C, D, E", "Falso / Verdadero"])

    # =================================================================
    # 🔑 SECCIÓN 2: LA LLAVE MAESTRA (Matriz de Respuestas)
    # =================================================================
    st.markdown("<br>", unsafe_allow_html=True)
    with st.container(border=True):
        st.markdown("### 🗝️ Llave Maestra de Respuestas")
        st.caption("Determine la respuesta correcta y el peso (puntaje) de cada pregunta. Esta matriz será el cerebro del Motor de Calificación.")

        opciones_validas = ["A", "B", "C", "D"]
        if tipo_opciones == "A, B, C, D, E": opciones_validas.append("E")
        elif tipo_opciones == "Falso / Verdadero": opciones_validas = ["V", "F"]

        if 'matriz_respuestas' not in st.session_state or len(st.session_state['matriz_respuestas']) != num_preguntas:
            datos_base = {
                "Pregunta": [f"Pregunta {i+1}" for i in range(num_preguntas)],
                "Respuesta Correcta": [opciones_validas[0] for _ in range(num_preguntas)],
                "Puntaje (Peso)": [1.0 for _ in range(num_preguntas)]
            }
            st.session_state['matriz_respuestas'] = pd.DataFrame(datos_base)

        df_llave_editada = st.data_editor(
            st.session_state['matriz_respuestas'],
            use_container_width=True,
            hide_index=True,
            column_config={
                "Pregunta": st.column_config.Column("Pregunta", disabled=True),
                "Respuesta Correcta": st.column_config.SelectboxColumn("Respuesta Correcta", options=opciones_validas, required=True),
                "Puntaje (Peso)": st.column_config.NumberColumn("Puntaje (Peso)", min_value=0.1, max_value=10.0, format="%.1f", required=True)
            }
        )

        puntaje_maximo_posible = df_llave_editada['Puntaje (Peso)'].sum()
        st.success(f"📊 **Puntaje Máximo Posible:** {puntaje_maximo_posible} puntos")

    # =================================================================
    # 💾 SECCIÓN 3: PROTOCOLO DE GUARDADO EN SUPABASE
    # =================================================================
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🚀 TRANSMITIR A LA BÓVEDA (SUPABASE)", type="primary", use_container_width=True):
        if not nombre_prueba.strip():
            st.error("⚠️ El nombre de la prueba no puede estar vacío.")
        else:
            with st.spinner("Estableciendo enlace seguro y transmitiendo datos..."):
                try:
                    # Estructuramos el paquete JSON exacto que pide nuestra tabla SQL
                    paquete_datos = {
                        "id_prueba": f"PR-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                        "nombre": nombre_prueba.strip(),
                        "materia": materia,
                        "fecha": fecha_prueba.strftime("%Y-%m-%d"),
                        "total_preguntas": int(num_preguntas),
                        "puntaje_maximo": float(puntaje_maximo_posible),
                        "llave_maestra": df_llave_editada.to_dict('records')
                    }
                    
                    # Disparamos a la base de datos
                    respuesta = supabase.table("pruebas_maestras").insert(paquete_datos).execute()
                    
                    st.balloons()
                    st.success(f"✅ ¡IMPACTO CONFIRMADO! Simulacro '{nombre_prueba}' ha sido guardado permanentemente en Supabase.")
                    
                except Exception as e:
                    st.error(f"💥 Error en la transmisión: {e}")

if __name__ == "__main__":
    ejecutar()
