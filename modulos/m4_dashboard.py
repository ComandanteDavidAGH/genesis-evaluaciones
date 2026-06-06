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
    .card-detalles { background-color: #f8f9fa; padding: 15px; border-radius: 8px; border: 1px solid #e0e0e0; }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("<h1 class='titulo-dashboard'>📊 Panel del Cuestionario y Analítica</h1>", unsafe_allow_html=True)
    st.caption("Ecosistema centralizado de control de evaluaciones, asistencia y diagnóstico de rendimiento.")

    try:
        supabase: Client = iniciar_conexion()
    except Exception:
        st.error("⚠️ Falla de conexión con el centro de datos.")
        return

    with st.spinner("Sincronizando registros académicos..."):
        try:
            res_respuestas = supabase.table("respuestas_estudiantes").select("*").execute()
            datos_respuestas = res_respuestas.data
            
            res_pruebas = supabase.table("pruebas_maestras").select("*").execute()
            datos_pruebas = res_pruebas.data

            res_estudiantes = supabase.table("estudiantes").select("nombre_completo, clases(nombre_clase)").execute()
            datos_estudiantes = res_estudiantes.data
        except Exception as e:
            st.error(f"💥 Error al conectar con las tablas: {e}")
            return

    if not datos_respuestas:
        st.info("📭 Aún no hay registros de estudiantes evaluados en el sistema.")
        return

    df_respuestas = pd.DataFrame(datos_respuestas)
    df_respuestas['fecha_formateada'] = pd.to_datetime(df_respuestas['created_at']).dt.strftime('%Y-%m-%d')

    if not datos_pruebas:
        st.info("📭 Cree una plantilla en el Módulo 1 para activar el panel.")
        return

    # Selector central del cuestionario (Estilo ZipGrade)
    opciones_pruebas = {f"{p['nombre']} - {p['materia']}": p for p in datos_pruebas}
    prueba_seleccionada = st.selectbox("📋 Seleccione el Cuestionario a Inspeccionar:", list(opciones_pruebas.keys()))
    
    datos_prueba_maestra = opciones_pruebas[prueba_seleccionada]
    id_prueba_target = datos_prueba_maestra["id_prueba"]
    llave_maestra = datos_prueba_maestra["llave_maestra"]
    
    # Filtrar respuestas específicas de este cuestionario
    df_filtrado = df_respuestas[df_respuestas['id_prueba'] == id_prueba_target]

    # =================================================================
    # 🗂️ BLOQUE A Y B: DISEÑO EN PARALELO (DETALLES VS DISTRIBUCIÓN)
    # =================================================================
    st.markdown("<br>", unsafe_allow_html=True)
    col_izq, col_der = st.columns([1, 1.3])

    with col_izq:
        st.markdown("#### 📝 Detalles del Cuestionario")
        fecha_evaluacion = df_filtrado['fecha_formateada'].iloc[0] if not df_filtrado.empty else "Sin registros"
        
        # Tabla limpia de especificaciones
        df_detalles_tabla = pd.DataFrame({
            "Especificación": ["Nombre del Examen", "Área / Asignatura", "Preguntas Totales", "Puntaje Máximo", "Último Escaneo"],
            "Detalle": [datos_prueba_maestra['nombre'], datos_prueba_maestra['materia'], f"{datos_prueba_maestra['total_preguntas']} Ítems", f"{datos_prueba_maestra['puntaje_maximo']:.1f} Pts", fecha_evaluacion]
        })
        st.dataframe(df_detalles_tabla, use_container_width=True, hide_index=True)
        
        # Botones de Acción Gerencial
        st.markdown("**Acciones Administrativas:**")
        ca1, ca2 = st.columns(2)
        with ca1: st.button("🗑️ Archivar Prueba", use_container_width=True)
        with ca2: st.button("🔗 Compartir Reporte", use_container_width=True)

    with col_der:
        st.markdown("#### 📊 Distribución de Puntuaciones (Escala Escolar)")
        if df_filtrado.empty:
            st.warning("No hay datos de distribución para graficar aún.")
        else:
            # Clasificar las notas en rangos de desempeño estándar
            def asignar_rango_desempeño(porc):
                if porc < 60.0: return "Desempeño Bajo (<60%)"
                elif porc < 80.0: return "Desempeño Básico (60%-79%)"
                elif porc < 90.0: return "Desempeño Alto (80%-89%)"
                else: return "Desempeño Superior (≥90%)"

            df_filtrado["Rango"] = df_filtrado["porcentaje"].apply(asignar_rango_desempeño)
            df_dist = df_filtrado.groupby("Rango").size().reset_index(name="Cantidad")
            
            # Histograma interactivo con Plotly
            fig_dist = px.bar(
                df_dist, x="Rango", y="Cantidad", text="Cantidad",
                color="Rango",
                color_discrete_map={
                    "Desempeño Bajo (<60%)": "#e63946",
                    "Desempeño Básico (60%-79%)": "#ffb703",
                    "Desempeño Alto (80%-89%)": "#219ebc",
                    "Desempeño Superior (≥90%)": "#2b9348"
                },
                category_orders={"Rango": ["Desempeño Bajo (<60%)", "Desempeño Básico (60%-79%)", "Desempeño Alto (80%-89%)", "Desempeño Superior (≥90%)"]}
            )
            fig_dist.update_traces(textposition='outside')
            fig_dist.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                xaxis_title="Nivel de Logro", yaxis_title="Número de Alumnos (Hojas)",
                showlegend=False, height=240, margin=dict(l=10, r=10, t=10, b=10)
            )
            st.plotly_chart(fig_dist, use_container_width=True, config={'displayModeBar': False})

    # =================================================================
    # 🕵️‍♂️ BLOQUE C: EL RASTREADOR DE ALUMNOS PENDIENTES (NUESTRO VALOR AGREGADO)
    # =================================================================
    st.markdown("<h3 class='sub-seccion'>🛑 Control de Asistencia y Evaluaciones Pendientes</h3>", unsafe_allow_html=True)
    
    if df_filtrado.empty:
        st.info("Suba datos al escáner para activar el control de asistencia.")
    else:
        # Extraer los nombres de los estudiantes que ya presentaron
        estudiantes_presentes = df_filtrado["estudiante"].dropna().tolist()
        
        # Identificar alumnos matriculados globalmente
        alumnos_pendientes = []
        if datos_estudiantes:
            for est in datos_estudiantes:
                nombre = est["nombre_completo"]
                curso = est["clases"]["nombre_clase"] if est["clases"] else "Sin Curso"
                
                # Formato idéntico al guardado por el escáner
                string_match = f"{nombre} ({curso})"
                
                if string_match not in estudiantes_presentes:
                    alumnos_pendientes.append({"Nombre del Alumno": nombre, "Curso / Grado": curso})

        if alumnos_pendientes:
            df_pendientes = pd.DataFrame(alumnos_pendientes)
            st.warning(f"⚠️ Se registran **{len(alumnos_pendientes)}** estudiantes matriculados que aún NO han presentado esta evaluación:")
            st.dataframe(df_pendientes, use_container_width=True, hide_index=True)
        else:
            st.success("🎉 ¡Asistencia Completa! Todos los estudiantes matriculados para este curso ya tienen su calificación registrada.")

    # =================================================================
    # 🧠 AUDITORÍA DE REACTIVOS Y COMPETENCIAS
    # =================================================================
    st.markdown("<h3 class='sub-seccion'>🧠 Diagnóstico Avanzado de Preguntas y Temas</h3>", unsafe_allow_html=True)
    
    if not df_filtrado.empty:
        analisis_preguntas = []
        for item in llave_maestra:
            pregunta_nombre = item["Pregunta"]
            respuesta_correcta = item["Respuesta Correcta"]
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
        
        # Gráfico de Preguntas Ordenado
        st.markdown("#### 📉 Índice de Error por Ítem (Orden Numérico Natural)")
        fig_items = px.bar(
            df_reactivos, x="Pregunta", y="Porcentaje de Error", color="Estado", text="Porcentaje de Error",
            hover_data={"Tema": True, "Porcentaje de Error": ":.1f%"},
            color_discrete_map={"🟢 Bajo Control (<20%)": "#2b9348", "🟡 En Observación (20%-49%)": "#ffb703", "🔴 Alerta Crítica (≥50%)": "#e63946"},
            category_orders={"Pregunta": df_reactivos["Pregunta"].tolist(), "Estado": ["🟢 Bajo Control (<20%)", "🟡 En Observación (20%-49%)", "🔴 Alerta Crítica (≥50%)"]}
        )
        fig_items.update_traces(texttemplate='%{text}%', textposition='outside')
        fig_items.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", yaxis=dict(range=[0, 115]), showlegend=False, height=240)
        st.plotly_chart(fig_items, use_container_width=True, config={'displayModeBar': False})
        
        # Conclusiones
        df_temas = df_reactivos.groupby("Tema", as_index=False)["Porcentaje de Error"].mean().round(1)
        temas_criticos = df_temas[df_temas["Porcentaje de Error"] >= 50.0]
        
        if not temas_criticos.empty:
            st.error(f"⚠️ **Conclusión Diagnóstica:** Se deben reforzar los componentes de: *{', '.join(temas_criticos['Tema'].tolist())}*.")
        else:
            st.success("✅ **Conclusión Diagnóstica:** El grupo asimiló los componentes de la evaluación dentro de los parámetros esperados.")
            
    st.markdown("---")
    st.markdown("<h3 class='sub-seccion'>📜 Historial Central de Calificaciones</h3>", unsafe_allow_html=True)
    df_visual = df_respuestas[['estudiante', 'nombre_prueba', 'puntaje_obtenido', 'puntaje_maximo', 'porcentaje', 'fecha_formateada']].copy()
    df_visual.columns = ['Estudiante / Curso', 'Evaluación', 'Puntaje', 'Máximo Posible', '% Efectividad', 'Fecha de Registro']
    st.dataframe(df_visual.sort_values(by="Fecha de Registro", ascending=False), use_container_width=True, hide_index=True)

if __name__ == "__main__":
    ejecutar()
