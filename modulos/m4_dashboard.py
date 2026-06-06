import streamlit as st
import pandas as pd
import plotly.express as px
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
    # 🎯 SECCIÓN 2: ANÁLISIS DE REACTIVOS CON SEMÁFORO INTELIGENTE
    # =================================================================
    st.markdown("<h3 class='sub-seccion'>🧠 Auditoría Diagnóstica de Reactivos (Fallas por Pregunta)</h3>", unsafe_allow_html=True)
    st.write("Identifique qué preguntas presentaron la mayor tasa de error en el grupo mediante el mapa de calor adaptativo.")

    if datos_pruebas:
        opciones_pruebas = {f"{p['nombre']} - {p['materia']}": p for p in datos_pruebas}
        prueba_seleccionada = st.selectbox("Elija la evaluación a auditar:", list(opciones_pruebas.keys()))
        
        datos_prueba_maestra = opciones_pruebas[prueba_seleccionada]
        id_prueba_target = datos_prueba_maestra["id_prueba"]
        llave_maestra = datos_prueba_maestra["llave_maestra"]
        
        df_filtrado = df_respuestas[df_respuestas['id_prueba'] == id_prueba_target]
        
        if df_filtrado.empty:
            st.warning("⚠️ No hay exámenes procesados todavía para esta plantilla de evaluación.")
        else:
            st.info(f"Análisis basado en **{len(df_filtrado)}** hojas escaneadas para este examen.")
            
            analisis_preguntas = []
            
            for item in llave_maestra:
                pregunta_nombre = item["Pregunta"]
                respuesta_correcta = item["Respuesta Correcta"]
                
                num_index = int(pregunta_nombre.replace("Pregunta ", ""))
                
                incorrectas = 0
                total_respuestas_pregunta = 0
                
                for _, fila in df_filtrado.iterrows():
                    json_respuestas = fila["respuestas_json"]
                    if json_respuestas and pregunta_nombre in json_respuestas:
                        total_respuestas_pregunta += 1
                        if json_respuestas[pregunta_nombre] != respuesta_correcta:
                            incorrectas += 1
                
                tasa_error = (incorrectas / total_respuestas_pregunta * 100) if total_respuestas_pregunta > 0 else 0
                
                if tasa_error < 20.0:
                    criticidad = "🟢 Bajo Control (<20%)"
                elif tasa_error < 50.0:
                    criticidad = "🟡 En Observación (20%-49%)"
                else:
                    criticidad = "🔴 Alerta Crítica (≥50%)"
                
                analisis_preguntas.append({
                    "Orden": num_index,
                    "Pregunta": f"P{num_index}",
                    "Porcentaje de Error": round(tasa_error, 1),
                    "Cantidad de Fallas": incorrectas,
                    "Estado": criticidad
                })
            
            df_reactivos = pd.DataFrame(analisis_preguntas).sort_values("Orden")
            
            st.markdown("#### 📉 Gráfico Dinámico: Índice de Error por Reactivo (%)")
            
            fig = px.bar(
                df_reactivos, 
                x="Pregunta", 
                y="Porcentaje de Error", 
                color="Estado",
                text="Porcentaje de Error",
                color_discrete_map={
                    "🟢 Bajo Control (<20%)": "#2b9348",
                    "🟡 En Observación (20%-49%)": "#ffb703",
                    "🔴 Alerta Crítica (≥50%)": "#e63946"
                },
                category_orders={"Estado": ["🟢 Bajo Control (<20%)", "🟡 En Observación (20%-49%)", "🔴 Alerta Crítica (≥50%)"]},
                labels={"Porcentaje de Error": "% Índice de Error", "Pregunta": "Reactivo Evaluado"}
            )
            
            fig.update_traces(texttemplate='%{text}%', textposition='outside')
            
            # 🔧 AJUSTE QUIRÚRGICO AQUÍ: Cambiado 'backgroundcolor' por 'paper_bgcolor'
            fig.update_layout(
                paper_bgcolor="#ffffff",
                plot_bgcolor="rgba(0,0,0,0)",
                yaxis=dict(range=[0, 110]),
                legend_title_text="Nivel de Criticidad",
                font=dict(family="Arial", size=12)
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            preguntas_criticas = df_reactivos[df_reactivos["Porcentaje de Error"] >= 50.0]
            if not preguntas_criticas.empty:
                st.error(f"⚠️ **Alerta de Refuerzo:** Las siguientes preguntas están en zona roja crítica: {', '.join(preguntas_criticas['Pregunta'].tolist())}. Se sugiere repasar estos componentes del aprendizaje.")
            else:
                st.success("✅ **Excelente balance:** Ninguna pregunta superó el umbral crítico de error. Los objetivos de la unidad se cumplieron con éxito.")
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
    main()
