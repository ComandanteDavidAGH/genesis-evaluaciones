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
# 🚀 EJECUCIÓN CENTRAL DEL MÓDULO DASHBOARD (MÓDULO 5 DEFINITIVO)
# =================================================================
def ejecutar():
    # 🎨 INYECCIÓN DE ALTA INGENIERÍA VISUAL (GÉNESIS ANALYTICS HUD)
    st.markdown("""
        <style>
        .titulo-genesis { color: #0d1b2a; font-family: 'Arial Black', sans-serif; font-size: 32px; margin-bottom: 0px; }
        .subtitulo-genesis { color: #d4af37; font-weight: bold; font-size: 13px; margin-top: -5px; letter-spacing: 1.5px; text-transform: uppercase; }
        .hud-container { display: flex; gap: 15px; margin-bottom: 25px; margin-top: 15px; }
        .hud-card { flex: 1; background: #ffffff; border-top: 3px solid #0d1b2a; border-radius: 4px 4px 12px 12px; padding: 12px 15px; text-align: center; box-shadow: 0 10px 25px rgba(13, 27, 42, 0.04); transition: all 0.2s ease; }
        .hud-card:hover { transform: translateY(-3px); box-shadow: 0 12px 30px rgba(212, 175, 55, 0.12); }
        .hud-label { font-size: 11px; font-weight: 800; color: #5c677d; letter-spacing: 1px; text-transform: uppercase; margin-bottom: 4px; }
        .hud-value { font-size: 32px; font-family: 'Arial Black', sans-serif; font-weight: 900; line-height: 1; color: #0d1b2a; }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("<p class='titulo-genesis'>📊 Dashboard Analítico e Informes</p>", unsafe_allow_html=True)
    st.markdown("<p class='subtitulo-genesis'>Consola Central de Rendimiento y Exportación de Matrices de Calificación</p>", unsafe_allow_html=True)
    st.markdown("---")

    try:
        supabase = iniciar_conexion()
    except Exception:
        st.error("⚠️ Falla de enlace con la base de datos central. Verifique credenciales.")
        return

    # =================================================================
    # 📥 EXTRACCIÓN DUAL Y CREACIÓN DEL PUENTE (CRUCE POR ID)
    # =================================================================
    with st.spinner("Sincronizando búnker de datos y cruzando telemetría..."):
        try:
            # 1. Extraemos los estudiantes y sus grados
            res_estudiantes = supabase.table("datos_estudiantes").select("ID_Estudiante, Nombre_Completo, Grado").execute()
            df_estudiantes = pd.DataFrame(res_estudiantes.data)
            
            # 2. Extraemos las notas consolidadas
            res_notas = supabase.table("notas_consolidadas").select("ID_Est, ASIGNATURA, P1, P2").execute()
            df_notas = pd.DataFrame(res_notas.data)
        except Exception as e:
            st.error(f"🚨 Error de lectura en la base de datos: {e}")
            return

    if df_estudiantes.empty or df_notas.empty:
        st.info("📭 Faltan datos en el sistema para realizar el cruce analítico.")
        return

    # Normalizamos columnas para unirlas de forma perfecta
    df_estudiantes = df_estudiantes.rename(columns={"ID_Estudiante": "ID_ESTUDIANTE", "Nombre_Completo": "NOMBRE_COMPLETO", "Grado": "GRADO"})
    df_notas = df_notas.rename(columns={"ID_Est": "ID_ESTUDIANTE", "ASIGNATURA": "ASIGNATURA", "P1": "P1", "P2": "P2"})

    # ¡El puente mágico! Unimos las dos tablas usando el ID del estudiante
    df_master = pd.merge(df_notas, df_estudiantes, on="ID_ESTUDIANTE", how="inner")

    if df_master.empty:
        st.warning("⚠️ No se encontraron coincidencias entre las listas de estudiantes y las notas cargadas.")
        return

    # =================================================================
    # 🎛️ DOBLE SELECTOR INTELIGENTE EN CASCADA
    # =================================================================
    col_sel1, col_sel2 = st.columns(2)
    
    with col_sel1:
        # Selector de Grado
        lista_grados = sorted(df_master['GRADO'].dropna().unique().tolist())
        grado_sel = st.selectbox("📂 1. SELECCIONE EL CURSO/GRADO:", lista_grados)
    
    if not grado_sel:
        return

    # Filtramos la data maestra por el grado seleccionado
    df_filtrado_grado = df_master[df_master['GRADO'] == grado_sel]

    with col_sel2:
        # Selector de Materia (Solo muestra las materias que ve ese grado)
        lista_materias = sorted(df_filtrado_grado['ASIGNATURA'].dropna().unique().tolist())
        materia_sel = st.selectbox("🎯 2. SELECCIONE LA ASIGNATURA:", lista_materias)

    if not materia_sel:
        return

    # Filtramos finalmente por la materia seleccionada
    df_final = df_filtrado_grado[df_filtrado_grado['ASIGNATURA'] == materia_sel].copy()

    # =================================================================
    # 🗃️ PROCESAMIENTO BIÓNICO DE DATOS (Cálculos y Rangos)
    # =================================================================
    filas_limpias = []
    conteo_niveles = {"Bajo (<60%)": 0, "Básico (60-79%)": 0, "Alto (80-89%)": 0, "Superior (≥90%)": 0}

    for _, fila in df_final.iterrows():
        estudiante = fila.get('NOMBRE_COMPLETO', 'ALUMNO ANÓNIMO')
        try:
            p1 = float(fila.get('P1', 0.0))
            p2 = float(fila.get('P2', 0.0))
            promedio = (p1 + p2) / 2
            pct = (promedio / 10) * 100  # Escala sobre 10
        except:
            p1, p2, promedio, pct = 0.0, 0.0, 0.0, 0.0
        
        # Asignación de rangos
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

    # Cálculo de métrica de aprobación para el HUD
    total_alumnos = len(filas_limpias)
    aprobados = sum([1 for x in filas_limpias if "APROBADO" in x["ESTADO ACADÉMICO"]])
    efectividad = round((aprobados / total_alumnos) * 100) if total_alumnos > 0 else 0

    # =================================================================
    # 📐 DESPLIEGUE VISUAL: HUD, TABLAS Y GRÁFICAS
    # =================================================================
    
    # 1. Paneles HUD Superiores
    st.markdown(f"""
        <div class="hud-container">
            <div class="hud-card" style="border-top-color: #0d1b2a;">
                <div class="hud-label">👥 ALUMNOS EN {grado_sel}</div>
                <div class="hud-value" style="color: #0d1b2a;">{total_alumnos}</div>
            </div>
            <div class="hud-card" style="border-top-color: #d4af37;">
                <div class="hud-label" style="color: #bfa12a;">📝 EVALUANDO MATERIA</div>
                <div class="hud-value" style="color: #d4af37; font-size: 26px;">{materia_sel}</div>
            </div>
            <div class="hud-card" style="border-top-color: #2b9348;">
                <div class="hud-label" style="color: #2b9348;">📈 EFECTIVIDAD INSTITUCIONAL</div>
                <div class="hud-value" style="color: #2b9348;">{efectividad}%</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # 2. Detalles y Gráfica
    c1, c2 = st.columns([1, 1.2])
    
    with c1:
        st.markdown("### 📝 Detalles de Operación")
        tabla_detalles = pd.DataFrame({
            "Especificación": ["Curso", "Asignatura", "Total Estudiantes", "Estado"],
            "Detalle": [grado_sel, materia_sel, total_alumnos, "ACTIVO"]
        })
        st.dataframe(tabla_detalles, use_container_width=True, hide_index=True)
        
        st.markdown("### 📥 Descargar Reportes:")
        if not df_informe.empty:
            buffer_csv = df_informe.to_csv(index=False).encode('utf-8')
            st.download_button("📄 Descargar CSV", buffer_csv, f"SABANA_{grado_sel}_{materia_sel}.csv", "text/csv", use_container_width=True)

    with c2:
        st.markdown("### 📊 Distribución de Puntuaciones")
        df_grafico = pd.DataFrame({"Nivel": list(conteo_niveles.keys()), "Hojas": list(conteo_niveles.values())})
        
        fig = px.bar(df_grafico, x="Nivel", y="Hojas", text_auto=True, color="Nivel")
        fig.update_layout(showlegend=False, margin=dict(l=10, r=10, t=10, b=10), xaxis_title=None)
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

    # 3. La Sabana Escaneada
    st.markdown("---")
    st.markdown(f"### 📋 Control de Asistencia y Sabana: {grado_sel} - {materia_sel}")
    
    if not df_informe.empty:
        st.dataframe(df_informe, use_container_width=True, hide_index=True)
    else:
        st.info("💡 Consola Vacía. Seleccione un curso y materia con registros válidos.")

if __name__ == "__main__":
    ejecutar()
