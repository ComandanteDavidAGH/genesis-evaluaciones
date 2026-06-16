import streamlit as st
import pandas as pd
import plotly.express as px
from supabase import create_client

# =================================================================
# 🔒 CONEXIÓN SEGURA
# =================================================================
def iniciar_conexion():
    url = st.secrets["SUPABASE_URL"].strip()
    key = st.secrets["SUPABASE_KEY"].strip()
    return create_client(url, key)

# =================================================================
# 🚀 EJECUCIÓN CENTRAL DEL MÓDULO DASHBOARD (MÓDULO 5)
# =================================================================
def ejecutar():
    # ✨ Títulos originales de tu Dashboard
    st.markdown("<h1 style='color: #0d1b2a; font-family: Arial Black;'>📊 Dashboard Analítico e Informes</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='color: #4a4a4a;'>Consola Central de Rendimiento y Exportación de Matrices de Calificación</h3>", unsafe_allow_html=True)
    st.markdown("---")

    try:
        supabase = iniciar_conexion()
    except Exception:
        st.error("⚠️ Falla de enlace con la base de datos central. Verifique credenciales.")
        return

    # 📥 CARGA DE DATOS DESDE notas_consolidadas
    with st.spinner("Sincronizando registros analíticos desde el búnker..."):
        try:
            res_notas = supabase.table("notas_consolidadas").select("*").execute()
            df_total = pd.DataFrame(res_notas.data)
        except Exception as e:
            st.error(f"🚨 Error de lectura en el búnker de datos: {e}")
            return

    if df_total.empty:
        st.info("📭 No se registran datos consolidados en el banco de datos para analizar.")
        return

    # Normalizamos columnas a mayúsculas para evitar errores de lectura
    df_total.columns = [c.upper() for c in df_total.columns]

    # =================================================================
    # 🎛️ SELECTOR GENERAL (Corregido a notas_consolidadas)
    # =================================================================
    if 'ASIGNATURA' in df_total.columns:
        lista_materias = sorted(df_total['ASIGNATURA'].dropna().unique().tolist())
    else:
        lista_materias = []

    materia_sel = st.selectbox("🎯 SELECCIONE LA ASIGNATURA PARA AUDITAR:", lista_materias)

    if not materia_sel:
        return

    # Filtramos la data únicamente para la materia seleccionada
    df_materia = df_total[df_total['ASIGNATURA'] == materia_sel].copy()

    # =================================================================
    # 🗃️ PROCESAMIENTO BIÓNICO DE DATOS (Cálculo de Promedios y Rangos)
    # =================================================================
    filas_limpias = []
    conteo_niveles = {"Bajo (<60%)": 0, "Básico (60-79%)": 0, "Alto (80-89%)": 0, "Superior (≥90%)": 0}

    for _, fila in df_materia.iterrows():
        estudiante = fila.get('NOMBRE_COMPLETO', 'ALUMNO ANÓNIMO')
        
        try:
            p1 = float(fila.get('P1', 0.0))
            p2 = float(fila.get('P2', 0.0))
            promedio = (p1 + p2) / 2
            pct = (promedio / 10) * 100  # Porcentaje basado en escala de 10
        except:
            p1, p2, promedio, pct = 0.0, 0.0, 0.0, 0.0
        
        # Asignación de rangos según la sabana
        if pct < 60.0:
            nivel, estado = "Bajo (<60%)", "REPROBADO ❌"
        elif 60.0 <= pct < 80.0:
            nivel, estado = "Básico (60-79%)", "APROBADO ✅"
        elif 80.0 <= pct < 90.0:
            nivel, estado = "Alto (80-89%)", "APROBADO ✅"
        else:
            nivel, estado = "Superior (≥90%)", "APROBADO ✅"
        
        conteo_niveles[nivel] += 1
        
        filas_limpias.append({
            "ESTUDIANTE MATRÍCULA": str(estudiante).upper(),
            "NOTA P1": round(p1, 1),
            "NOTA P2": round(p2, 1),
            "PROMEDIO": round(promedio, 1),
            "RANGO COGNITIVO": nivel,
            "ESTADO ACADÉMICO": estado
        })

    df_informe = pd.DataFrame(filas_limpias)
    if not df_informe.empty:
        df_informe = df_informe.sort_values(by="ESTUDIANTE MATRÍCULA")

    # =================================================================
    # 📐 DISTRIBUCIÓN GRÁFICA Y PANELES DE DETALLE
    # =================================================================
    c1, c2 = st.columns([1, 1.2])
    
    with c1:
        st.markdown("### 📝 Detalles de Operación")
        # Tabla de Especificaciones idéntica a tu diseño original
        tabla_detalles = pd.DataFrame({
            "Especificación": ["Asignatura", "Total Estudiantes", "Estado"],
            "Detalle": [materia_sel, len(df_materia), "ACTIVO"]
        })
        st.dataframe(tabla_detalles, use_container_width=True, hide_index=True)
        
        st.markdown("### 📥 Descargar Reportes Masivos:")
        if not df_informe.empty:
            buffer_csv = df_informe.to_csv(index=False).encode('utf-8')
            st.download_button("📄 Descargar CSV", buffer_csv, f"REPORTE_{materia_sel}.csv", "text/csv", use_container_width=True)

    with c2:
        st.markdown("### 📊 Distribución de Puntuaciones")
        df_grafico = pd.DataFrame({"Nivel": list(conteo_niveles.keys()), "Hojas": list(conteo_niveles.values())})
        
        # Gráfica de barras de rendimiento
        fig = px.bar(df_grafico, x="Nivel", y="Hojas", text_auto=True, color="Nivel")
        fig.update_layout(showlegend=False, margin=dict(l=10, r=10, t=10, b=10), xaxis_title=None)
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

    st.markdown("---")
    st.markdown("### 📋 Control de Asistencia y Sabana Escaneada")
    
    if not df_informe.empty:
        st.dataframe(df_informe, use_container_width=True, hide_index=True)
    else:
        st.info("💡 Consola Vacía. Seleccione una materia con registros.")

if __name__ == "__main__":
    ejecutar()
