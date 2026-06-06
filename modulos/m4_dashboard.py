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
    .sub-seccion { color: #1b263b; font-family: 'Arial'; margin-top: 25px; border-left: 4px solid #d4af37; padding-left: 10px; }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("<h1 class='titulo-dashboard'>📊 Centro de Inteligencia: Dashboard Analítico</h1>", unsafe_allow_html=True)
    st.caption("Panel de control gerencial para el análisis del rendimiento académico y diagnóstico temático por competencias.")

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
    # 🌍 RESUMEN INSTITUCIONAL
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
    # 🎯 AUDITORÍA DIAGNÓSTICA DE REACTIVOS Y COMPETENCIAS
    # =================================================================
    st.markdown("<h3 class='sub-seccion'>🧠 Auditoría Diagnóstica de Reactivos y Competencias</h3>", unsafe_allow_html=True)

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
            st.info(f"Análisis basado en **{len(df_filtrado)}** hojas escaneadas.")
            
            analisis_preguntas = []
            for item in llave_maestra:
                pregunta_nombre = item["Pregunta"]
                respuesta_correcta = item["Respuesta Correcta"]
                
                # 🛡️ RETROCOMPATIBILIDAD INTEGRADA: Si la plantilla vieja no tenía tema, asigna "Concepto General"
                tema_asignado = item.get("Tema", "Concepto General")
                
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
                
                if tasa_error < 20.0: criticidad = "🟢 Bajo Control (<20%)"
                elif tasa_error < 50.0: criticidad = "🟡 En Observación (20%-49%)"
                else: criticidad = "🔴 Alerta Crítica (≥50%)"
                
                analisis_preguntas.append({
                    "Orden": num_index,
                    "Pregunta": f"P{num_index}",
                    "Tema": tema_asignado,
                    "Porcentaje de Error": round(tasa_error, 1),
                    "Estado": criticidad
                })
            
            df_reactivos = pd.DataFrame(analisis_preguntas).sort_values("Orden")
            
            # --- REPORTE 1: GRÁFICO POR PREGUNTA ---
            st.markdown("#### 📉 Gráfico 1: Índice de Error por Ítem (Orden Numérico)")
            fig_items = px.bar(
                df_reactivos, x="Pregunta", y="Porcentaje de Error", color="Estado", text="Porcentaje de Error",
                hover_data={"Tema": True, "Porcentaje de Error": ":.1f%"}, # El tema ahora se ve al pasar el cursor
                color_discrete_map={"🟢 Bajo Control (<20%)": "#2b9348", "🟡 En Observación (20%-49%)": "#ffb703", "🔴 Alerta Crítica (≥50%)": "#e63946"},
                category_orders={"Estado": ["🟢 Bajo Control (<20%)", "🟡 En Observación (20%-49%)", "🔴 Alerta Crítica (≥50%)"]}
            )
            fig_items.update_traces(texttemplate='%{text}%', textposition='outside')
            fig_items.update_layout(paper_bgcolor="#ffffff", plot_bgcolor="rgba(0,0,0,0)", yaxis=dict(range=[0, 115]), legend_title_text="Criticidad")
            st.plotly_chart(fig_items, use_container_width=True)
            
            # --- REPORTE 2: EL PEDIDO DE LA DIRECCIÓN (CONSOLIDADO POR TEMAS) ---
            st.markdown("#### 🧠 Gráfico 2: Diagnóstico Consolidado por Temas Académicos")
            st.write("Agrupa el desempeño de todas las preguntas asociadas a un mismo componente conceptual.")
            
            # Calculamos el promedio de error que tiene cada tema agrupado
            df_temas = df_reactivos.groupby("Tema", as_index=False)["Porcentaje de Error"].mean()
            df_temas["Porcentaje de Error"] = df_temas["Porcentaje de Error"].round(1)
            
            def asignar_color_tema(val):
                if val < 20.0: return "🟢 Desempeño Alto"
                elif val < 50.0: return "🟡 Desempeño Medio"
                else: return "🔴 Requiere Refuerzo"
                
            df_temas["Estado Competencia"] = df_temas["Porcentaje de Error"].apply(asignar_color_tema)
            
            fig_temas = px.bar(
                df_temas, x="Porcentaje de Error", y="Tema", color="Estado Competencia", text="Porcentaje de Error",
                orientation='h', # Gráfico horizontal elegante para leer textos largos de temas
                color_discrete_map={"🟢 Desempeño Alto": "#2b9348", "🟡 Desempeño Medio": "#ffb703", "🔴 Requiere Refuerzo": "#e63946"}
            )
            fig_temas.update_traces(texttemplate='%{text}%', textposition='outside')
            fig_temas.update_layout(paper_bgcolor="#ffffff", plot_bgcolor="rgba(0,0,0,0)", xaxis=dict(range=[0, 115]), legend_title_text="Estado")
            st.plotly_chart(fig_temas, use_container_width=True)

            # Alertas dinámicas temáticas
            criticas = df_reactivos[df_reactivos["Porcentaje de Error"] >= 50.0]
            if not criticas.empty:
                st.error(f"⚠️ **Alerta Curricular:** Se detectaron debilidades graves en los siguientes componentes: *{', '.join(criticas['Tema'].unique())}* (Preguntas: {', '.join(criticas['Pregunta'].tolist())}).")
            else:
                st.success("✅ **Felicidades:** El grupo demuestra un equilibrio cognitivo sólido en todas las competencias evaluadas.")
    else:
        st.info("No hay plantillas maestras registradas.")

    st.markdown("---")
    st.markdown("<h3 class='sub-seccion'>📜 Historial Central de Calificaciones</h3>", unsafe_allow_html=True)
    df_visual = df_respuestas[['estudiante', 'nombre_prueba', 'puntaje_obtenido', 'puntaje_maximo', 'porcentaje', 'fecha_formateada']].copy()
    df_visual.columns = ['Estudiante / Curso', 'Evaluación', 'Puntaje', 'Máximo Posible', '% Efectividad', 'Fecha de Registro']
    st.dataframe(df_visual.sort_values(by="Fecha de Registro", ascending=False), use_container_width=True, hide_index=True)

if __name__ == "__main__":
    ejecutar()
