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
    st.caption("Panel de control simplificado para el diagnóstico del rendimiento académico institucional.")

    try:
        supabase: Client = iniciar_conexion()
    except Exception:
        st.error("⚠️ Falla de conexión con el centro de datos.")
        return

    with st.spinner("Cargando métricas de rendimiento..."):
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
    # 🌍 SECCIÓN 1: VISTA GLOBAL INSTITUCIONAL
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
    # 🎯 SECCIÓN 2: DIAGNÓSTICO POR COMPETENCIAS (UX SIMPLIFICADA)
    # =================================================================
    st.markdown("<h3 class='sub-seccion'>🧠 Diagnóstico por Temas Académicos</h3>", unsafe_allow_html=True)
    st.write("Visualice el porcentaje de error promedio del grupo. Entre más corta sea la barra, mejor es el desempeño.")

    if datos_pruebas:
        opciones_pruebas = {f"{p['nombre']} - {p['materia']}": p for p in datos_pruebas}
        prueba_seleccionada = st.selectbox("Seleccione la evaluación que desea revisar:", list(opciones_pruebas.keys()))
        
        datos_prueba_maestra = opciones_pruebas[prueba_seleccionada]
        id_prueba_target = datos_prueba_maestra["id_prueba"]
        llave_maestra = datos_prueba_maestra["llave_maestra"]
        
        df_filtrado = df_respuestas[df_respuestas['id_prueba'] == id_prueba_target]
        
        if df_filtrado.empty:
            st.warning("⚠️ No se han escaneado hojas de respuestas para esta evaluación todavía.")
        else:
            # Procesar datos y calcular medias por tema
            analisis_preguntas = []
            for item in llave_maestra:
                pregunta_nombre = item["Pregunta"]
                respuesta_correcta = item["Respuesta Correcta"]
                tema_asignado = item.get("Tema", "Concepto General")
                
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
                    "Tema": tema_asignado,
                    "Porcentaje de Error": tasa_error
                })
            
            # Agrupar limpiamente por componentes conceptuales usando Pandas
            df_reactivos = pd.DataFrame(analisis_preguntas)
            df_temas = df_reactivos.groupby("Tema", as_index=False)["Porcentaje de Error"].mean()
            df_temas["Porcentaje de Error"] = df_temas["Porcentaje de Error"].round(1)
            
            # Clasificación semántica del Semáforo
            def clasificar_estado(val):
                if val < 20.0: return "🟢 Desempeño Alto (Error < 20%)"
                elif val < 50.0: return "🟡 Desempeño Medio (Error 20%-49%)"
                else: return "🔴 Requiere Refuerzo (Error ≥ 50%)"
                
            df_temas["Estado"] = df_temas["Porcentaje de Error"].apply(clasificar_estado)
            
            # Configuración de gráfico Plotly ultra-limpio y adaptativo
            fig_temas = px.bar(
                df_temas, 
                x="Porcentaje de Error", 
                y="Tema", 
                color="Estado", 
                text="Porcentaje de Error",
                orientation='h',
                color_discrete_map={
                    "🟢 Desempeño Alto (Error < 20%)": "#2b9348",
                    "🟡 Desempeño Medio (Error 20%-49%)": "#ffb703",
                    "🔴 Requiere Refuerzo (Error ≥ 50%)": "#e63946"
                }
            )
            
            # Optimización estética para eliminar duplicidades y ajustar proporciones
            fig_temas.update_traces(texttemplate=' %{text}%', textposition='outside')
            
            # Ajustar la altura dinámicamente según el número de temas para evitar deformaciones
            altura_grafico = max(180, len(df_temas) * 70)
            
            fig_temas.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                xaxis=dict(range=[0, 120], title="Porcentaje de Error Promedio del Grupo", showgrid=True, gridcolor="#e0e0e0"),
                yaxis=dict(title="Temas Evaluados"),
                legend=dict(title="Escala de Rendimiento", orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                height=altura_grafico,
                margin=dict(l=20, r=20, t=50, b=20)
            )
            
            st.plotly_chart(fig_temas, use_container_width=True, config={'displayModeBar': False})

            # =================================================================
            # 🛡️ SISTEMA DE ALERTAS COHERENTE (UX SIN CONTRADICCIONES)
            # =================================================================
            st.markdown("#### 📢 Conclusiones del Diagnóstico Automático")
            
            temas_criticos = df_temas[df_temas["Porcentaje de Error"] >= 50.0]
            temas_medios = df_temas[(df_temas["Porcentaje de Error"] >= 20.0) & (df_temas["Porcentaje de Error"] < 50.0)]
            
            # Las alertas ahora corresponden estrictamente al color de las barras
            if not temas_criticos.empty:
                lista_criticos = ", ".join([f"*{t}*" for t in temas_criticos["Tema"].tolist()])
                st.error(f"⚠️ **Atención Necesaria:** Se encontraron vacíos de aprendizaje críticos en: {lista_criticos}. Se recomienda priorizar el repaso de estos conceptos.")
            elif not temas_medios.empty:
                lista_medios = ", ".join([f"*{t}*" for t in temas_medios["Tema"].tolist()])
                st.warning(f"💡 **Sugerencia de Repaso:** El grupo muestra dudas moderadas en: {lista_medios}. Ejercicios complementarios ayudarán a consolidar el tema.")
            else:
                st.success("✅ **Rendimiento Excelente:** Todo el contenido evaluado está bajo control. El grupo asimiló los conceptos de forma satisfactoria.")
                
    else:
        st.info("No hay evaluaciones registradas en el sistema.")

    st.markdown("---")

    # =================================================================
    # 📜 HISTORIAL DE NOTAS
    # =================================================================
    st.markdown("<h3 class='sub-seccion'>📜 Historial Central de Calificaciones</h3>", unsafe_allow_html=True)
    df_visual = df_respuestas[['estudiante', 'nombre_prueba', 'puntaje_obtenido', 'puntaje_maximo', 'porcentaje', 'fecha_formateada']].copy()
    df_visual.columns = ['Estudiante / Curso', 'Evaluación', 'Puntaje', 'Máximo Posible', '% Efectividad', 'Fecha de Registro']
    st.dataframe(df_visual.sort_values(by="Fecha de Registro", ascending=False), use_container_width=True, hide_index=True)

if __name__ == "__main__":
    ejecutar()
