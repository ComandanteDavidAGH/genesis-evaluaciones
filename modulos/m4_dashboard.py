import streamlit as st
import pandas as pd
import plotly.express as px
import io
from supabase import create_client
from estilos_globales import inyectar_estilos_omega

# =================================================================
# 🔒 CONEXIÓN AL BÚNKER DE DATOS INSTITUCIONAL
# =================================================================
def iniciar_conexion():
    """Establece conexión segura con la base de datos Supabase."""
    url = st.secrets["SUPABASE_URL"].strip()
    key = st.secrets["SUPABASE_KEY"].strip()
    return create_client(url, key)

# =================================================================
# 🛡️ SENSOR DETECTOR INALÁMBRICO DE COLUMNAS ( Fail-Safe )
# =================================================================
def buscar_campo(diccionario, nombre_campo, predeterminado=""):
    """Busca un campo en un diccionario de forma segura y sin mayúsculas."""
    if diccionario is None:
        return predeterminado
    try:
        if hasattr(diccionario, 'empty') and diccionario.empty:
            return predeterminado
    except:
        pass
    try:
        for llave, valor in diccionario.items():
            if str(llave).lower() == nombre_campo.lower():
                if valor is not None and str(valor).strip().lower() not in ['none', 'null', '']:
                    return valor
    except:
        pass
    return predeterminado

# =================================================================
# 🚀 EJECUCIÓN CENTRAL DEL MÓDULO DASHBOARD
# =================================================================
def ejecutar():
    # ⚡ Inyección visual unificada Génesis Omega Pro (Escudo Estético)
    inyectar_estilos_omega()

    # ✨ Títulos Corregidos con Estilo Omega Pro
    st.markdown("<h1 class='titulo-dash'>📊 Dashboard Analítico e Informes</h1>", unsafe_allow_html=True)
    st.markdown("<h3 class='subtitulo-dash'>Consola Central de Rendimiento y Exportación de Matrices de Calificación</h3>", unsafe_allow_html=True)
    st.markdown("---")

    try:
        supabase = iniciar_conexion()
    except Exception:
        st.error("⚠️ Falla de enlace con la base de datos central. Verifique credenciales.")
        return

    # 📥 SINCRONIZACIÓN DE COMPONENTES CRIPTOGRÁFICOS
    with st.spinner("Sincronizando registros analíticos desde el búnker..."):
        try:
            # CAMBIO: Obtenemos el consolidado desde notas_consolidadas
            res_notas = supabase.table("notas_consolidadas").select("*").execute()
            notas_raw = res_notas.data
        except Exception as e:
            st.error(f"🚨 Error de lectura en el búnker de datos: {e}")
            return

    if not notas_raw:
        st.info("📭 No se registran datos en el banco de datos para analizar.")
        return

    # =================================================================
    # 🎛️ SELECTOR GENERAL
    # =================================================================
    df_raw = pd.DataFrame(notas_raw)
    df_raw.columns = [c.lower() for c in df_raw.columns]
    lista_materias = sorted(df_raw['asignatura'].dropna().unique().tolist())

    # Widget Selector
    materia_sel = st.selectbox("🎯 SELECCIONE LA ASIGNATURA PARA AUDITAR:", lista_materias)

    # =================================================================
    # 🗃️ PROCESAMIENTO BIÓNICO DE DATOS
    # =================================================================
    df_notas = df_raw[df_raw['asignatura'] == materia_sel]

    # Contenedores de resultados consolidados
    df_informe_limpio = pd.DataFrame()
    conteo_niveles = {"Bajo (<60%)": 0, "Básico (60-79%)": 0, "Alto (80-89%)": 0, "Superior (≥90%)": 0}

    # Iteración y Limpieza del Puente de Notas
    if not df_notas.empty:
        filas_limpias = []
        for _, fila in df_notas.iterrows():
            estudiante_str = str(buscar_campo(fila, 'nombre_completo', 'ALUMNO ANÓNIMO'))
            
            try:
                # Ajusta según tus columnas reales (p1, p2, etc)
                p1 = float(buscar_campo(fila, 'p1', 0.0))
                p2 = float(buscar_campo(fila, 'p2', 0.0))
                promedio = (p1 + p2) / 2
                pct = (promedio / 10) * 100 
            except:
                pct, promedio = 0.0, 0.0
            
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
                "ESTUDIANTE MATRÍCULA": estudiante_str.upper(),
                "NOTA P1": p1,
                "NOTA P2": p2,
                "PROMEDIO": round(promedio, 2),
                "RANGO COGNITIVO": nivel,
                "ESTADO ACADÉMICO": estado
            })
        
        if filas_limpias:
            df_informe_limpio = pd.DataFrame(filas_limpias).sort_values(by="ESTUDIANTE MATRÍCULA")

    # =================================================================
    # 📐 DISTRIBUCIÓN GRÁFICA Y PANELES DE DETALLE
    # =================================================================
    c1, c2 = st.columns([1, 1.2])
    
    with c1:
        st.markdown("### 📝 Detalles de Operación")
        # Tabla de Especificaciones
        tabla_detalles = pd.DataFrame({
            "Especificación": ["Asignatura", "Total Estudiantes", "Estado"],
            "Detalle": [materia_sel, len(df_notas), "ACTIVO"]
        })
        st.dataframe(tabla_detalles, use_container_width=True, hide_index=True)
        
        st.markdown("### 📥 Descargar Reportes Masivos:")
        if not df_informe_limpio.empty:
            buffer_csv = df_informe_limpio.to_csv(index=False).encode('utf-8')
            st.download_button("📄 Descargar CSV", buffer_csv, f"REPORTE_{materia_sel}.csv", "text/csv", use_container_width=True)

    with c2:
        st.markdown("### 📊 Distribución de Puntuaciones")
        df_grafico = pd.DataFrame({"Nivel": list(conteo_niveles.keys()), "Hojas": list(conteo_niveles.values())})
        
        fig = px.bar(df_grafico, x="Nivel", y="Hojas", color="Nivel", text_auto=True, height=320)
        fig.update_layout(showlegend=False, margin=dict(l=10, r=10, t=10, b=10), xaxis_title=None)
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

    st.markdown("---")
    st.markdown("### 📋 Control de Asistencia y Sabana Escaneada")
    
    if not df_informe_limpio.empty:
        st.data_editor(df_informe_limpio, use_container_width=True, hide_index=True, disabled=True)
    else:
        st.info("💡 Consola Vacía.")

if __name__ == "__main__":
    ejecutar()
