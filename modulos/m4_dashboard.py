import streamlit as st
import pandas as pd
from supabase import create_client, Client

# =================================================================
# 🔌 CONEXIÓN AL CENTRO DE DATOS
# =================================================================
@st.cache_resource
def iniciar_conexion():
    url = st.secrets["SUPABASE_URL"].replace('"', '').replace("'", "").strip()
    key = st.secrets["SUPABASE_KEY"].replace('"', '').replace("'", "").strip()
    return create_client(url, key)

def ejecutar():
    st.markdown("""
    <style>
    .titulo-dashboard { color: #0d1b2a; border-bottom: 3px solid #d4af37; padding-bottom: 5px; font-family: 'Arial Black'; }
    .sub-seccion { color: #1b263b; font-family: 'Arial'; margin-top: 20px; border-left: 4px solid #d4af37; padding-left: 10px; }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("<h1 class='titulo-dashboard'>📊 Centro de Inteligencia: Dashboard Analítico</h1>", unsafe_allow_html=True)
    st.caption("Panel de control gerencial para el análisis del rendimiento académico y diagnóstico de reactivos.")

    try:
        supabase: Client = iniciar_conexion()
    except Exception:
        st.error("⚠️ Falla de conexión con el centro de datos.")
        return

    # Descarga paralela de respuestas y plantillas maestras
    with st.spinner("Extrayendo métricas desde el centro de datos..."):
        try:
            res_respuestas = supabase.table("respuestas_estudiantes").select("*").execute()
            datos_respuestas = res_respuestas.data
            
            res_pruebas = supabase.table("pruebas_maestras").select("*").execute()
            datos_pruebas = res_pruebas.data
        except Exception as e:
            st.error(f"💥 Error al conectar con las tablas: {e}")
            return

    if not datos_respuestas:
        st.info("📭 Aún no hay registros de estudiantes evaluados para generar estadísticas.")
        return

    df_respuestas = pd.DataFrame(datos_respuestas)
    df_respuestas['fecha_formateada'] = pd.to_datetime(df_respuestas['created_at']).dt.strftime('%Y-%m-%d %H:%M')

    # =================================================================
    # 📋 SECCIÓN 1: VISTA GLOBAL INSTITUCIONAL
    # =================================================================
    st.markdown("<h3 class='sub-seccion'>🌍 Resumen General de Rendimiento</h3>", unsafe_allow_html=True)
    
    total_evaluados = len(df_respuestas)
    promedio_general = df_respuestas['porcentaje'].mean()
    aprobados = len(df_respuestas[df_respuestas['porcentaje'] >= 60.0])
    tasa_aprobacion = (aprobados / total_evaluados) * 100 if total_evaluados > 0 else 0

    c1, c2, c3 = st.columns(3)
    with c1: st.metric(label="👥 Total Calificaciones Procesadas", value=f"{total_evaluados} Hojas")
    with c2: st.metric(label="📈 Promedio General de Efectividad", value=f"{promedio_general:.1f}%")
    with c3: st.metric(label="🎯 Tasa General de Aprobación", value=f"{tasa_aprobacion:.1f}%", delta=f"{aprobados} Alumnos aprobados")

    st.markdown("---")

    # =================================================================
    # 🎯 SECCIÓN 2: ANÁLISIS DE REACTIVOS (LA VENTAJA COMPETITIVA)
    # =================================================================
    st.markdown("<h3 class='sub-seccion'>🧠 Auditoría Diagnóstica de Reactivos (Fallas por Pregunta)</h3>", unsafe_allow_html=True)
    st.write("Seleccione una evaluación para identificar qué preguntas específicas presentaron la mayor tasa de error en el grupo.")

    if datos_pruebas:
        opciones_pruebas = {f"{p['nombre']} - {p['materia']}": p for p in datos_pruebas}
        prueba_seleccionada = st.selectbox("Elija la evaluación a auditar:", list(opciones_pruebas.keys()))
        
        datos_prueba_maestra = opciones_pruebas[prueba_seleccionada]
        id_prueba_target = datos_prueba_maestra["id_prueba"]
        llave_maestra = datos_prueba_maestra["llave_maestra"]
        
        # Filtrar respuestas solo de la prueba seleccionada
        df_filtrado = df_respuestas[df_respuestas['id_prueba'] == id_prueba_target]
        
        if df_filtrado.empty:
            st.warning("⚠️ No hay exámenes procesados todavía para esta plantilla de evaluación.")
        else:
            st.info(f"Análisis basado en **{len(df_filtrado)}** hojas escaneadas para este examen.")
            
            # Algoritmo de cálculo de índices de error por pregunta
            analisis_preguntas = []
            
            for item in llave_maestra:
                pregunta_nombre = item["Pregunta"]
                respuesta_correcta = item["Respuesta Correcta"]
                
                incorrectas = 0
                total_respuestas_pregunta = 0
                
                for _, fila in df_filtrado.iterrows():
                    json_respuestas = fila["respuestas_json"]
                    if json_respuestas and pregunta_nombre in json_respuestas:
                        total_respuestas_pregunta += 1
                        if json_respuestas[pregunta_nombre] != respuesta_correcta:
                            incorrectas += 1
                
                tasa_error = (incorrectas / total_respuestas_pregunta * 100) if total_respuestas_pregunta > 0 else 0
                analisis_preguntas.append({
                    "Pregunta": pregunta_nombre.replace("Pregunta ", "P"),
                    "Porcentaje de Error": round(tasa_error, 1),
                    "Cantidad de Fallas": incorrectas
                })
            
            df_reactivos = pd.DataFrame(analisis_preguntas)
            
            # Despliegue gráfico del mapa de calor de errores
            st.markdown("#### 📉 Gráfico: Índice de Error por Reactivo (%)")
            st.caption("Las barras más altas representan los conceptos donde los estudiantes fallaron más. ¡Atención prioritaria aquí!")
            
            # Renderizar gráfico de barras nativo de Streamlit optimizado
            df_grafico = df_reactivos.set_index("Pregunta")[["Porcentaje de Error"]]
            st.bar_chart(df_grafico, color="#d4af37", use_container_width=True)
            
            # Alertas pedagógicas automáticas para el docente
            preguntas_criticas = df_reactivos[df_reactivos["Porcentaje de Error"] >= 50.0]
            if not preguntas_criticas.empty:
                st.error(f"⚠️ **Alerta de Refuerzo:** Las siguientes preguntas superaron el 50% de error en el grupo: {', '.join(preguntas_criticas['Pregunta'].tolist())}. Se sugiere repasar estos temas.")
            else:
                st.success("✅ **Excelente balance:** Ninguna pregunta supera el 50% de error. El grupo asimiló los contenidos de forma uniforme.")
    else:
        st.info("No hay plantillas maestras registradas.")

    st.markdown("---")

    # =================================================================
    # 📜 SECCIÓN 3: BITÁCORA HISTÓRICA INSTITUCIONAL
    # =================================================================
    st.markdown("<h3 class='sub-seccion'>📜 Historial Central de Calificaciones</h3>", unsafe_allow_html=True)
    df_visual = df_respuestas[['estudiante', 'nombre_prueba', 'puntaje_obtenido', 'puntaje_maximo', 'porcentaje', 'fecha_formateada']].copy()
    df_visual.columns = ['Estudiante / Curso', 'Evaluación', 'Puntaje', 'Máximo Posible', '% Efectividad', 'Fecha de Registro']
    
    st.dataframe(
        df_visual.sort_values(by="Fecha de Registro", ascending=False),
        use_container_width=True,
        hide_index=True
    )

if __name__ == "__main__":
    ejecutar()
