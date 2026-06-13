import streamlit as st
import pandas as pd
from supabase import create_client, Client

# =================================================================
# 🔒 CONEXIÓN SEGURA CON EL BÚNKER DE PRODUCCIÓN
# =================================================================
def iniciar_conexion():
    url = st.secrets["SUPABASE_URL"].strip()
    key = st.secrets["SUPABASE_KEY"].strip()
    return create_client(url, key)

def ejecutar():
    # 🎨 INYECCIÓN DE ALTA INGENIERÍA VISUAL (GÉNESIS ANALYTICS HUD)
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
            font-size: 13px;
            margin-top: -5px;
            letter-spacing: 1.5px;
            text-transform: uppercase;
        }
        
        .hud-container {
            display: flex;
            gap: 15px;
            margin-bottom: 25px;
            margin-top: 15px;
        }
        .hud-card {
            flex: 1;
            background: #ffffff;
            border-top: 3px solid #0d1b2a;
            border-radius: 4px 4px 12px 12px;
            padding: 12px 15px;
            text-align: center;
            box-shadow: 0 10px 25px rgba(13, 27, 42, 0.04);
            transition: all 0.2s ease;
        }
        .hud-card:hover {
            transform: translateY(-3px);
            box-shadow: 0 12px 30px rgba(212, 175, 55, 0.12);
        }
        .hud-label {
            font-size: 11px;
            font-weight: 800;
            color: #5c677d;
            letter-spacing: 1px;
            text-transform: uppercase;
            margin-bottom: 4px;
        }
        .hud-value {
            font-size: 32px;
            font-family: 'Arial Black', sans-serif;
            font-weight: 900;
            line-height: 1;
            color: #0d1b2a;
        }
        
        .contenedor-matriz {
            background-color: #ffffff;
            border-radius: 12px;
            border: 1px solid #e5e5e5;
            border-top: 4px solid #0d1b2a;
            padding: 20px;
            box-shadow: 0 8px 30px rgba(0,0,0,0.02);
            margin-top: 20px;
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("<p class='titulo-genesis'>📊 Panel del Cuestionario y Analítica</p>", unsafe_allow_html=True)
    st.markdown("<p class='subtitulo-genesis'>Ecosistema Centralizado de Control de Evaluaciones e Inteligencia Académica</p>", unsafe_allow_html=True)
    st.markdown("---")

    # Pestañas institucionales limpias
    tab1, tab2 = st.tabs(["📊 Analítica General", "📂 Consolidación por Período (Migrar)"])

    with tab1:
        try:
            supabase = iniciar_conexion()
            
            # =================================================================
            # 🛰️ EXTRACTOR EN RÁFAGAS CORREGIDO (Apuntando a data_estudiantes)
            # =================================================================
            estudiantes_base = []
            offset = 0
            chunk_size = 1000  
            
            with st.spinner("Compilando telemetría analítica..."):
                while True:
                    # CORREGIDO: Se cambia 'estudiantes' por 'data_estudiantes' y se añade orden
                    resultado = supabase.table("data_estudiantes")\
                        .select('ID_Estudiante, Nombre_Completo, Grado, Grupo')\
                        .order('ID_Estudiante')\
                        .range(offset, offset + chunk_size - 1)\
                        .execute()
                    
                    if not resultado.data:
                        break
                        
                    estudiantes_base.extend(resultado.data)
                    
                    if len(resultado.data) < chunk_size:
                        break
                        
                    offset += chunk_size  
                    
        except Exception as e:
            st.error(f"🚨 Error en la sincronización de tablas: {e}")
            return

        if estudiantes_base:
            df_unicos = pd.DataFrame(estudiantes_base).drop_duplicates(subset=["ID_Estudiante"])
            total_alumnos = len(df_unicos)

            # HUD de Control Analítico Superior
            st.markdown(f"""
                <div class="hud-container">
                    <div class="hud-card" style="border-top-color: #0d1b2a;">
                        <div class="hud-label">👥 AUDITORÍA DE ALUMNOS</div>
                        <div class="hud-value" style="color: #0d1b2a;">{total_alumnos}</div>
                    </div>
                    <div class="hud-card" style="border-top-color: #d4af37;">
                        <div class="hud-label" style="color: #bfa12a;">📝 EVALUACIONES PROCESADAS</div>
                        <div class="hud-value" style="color: #d4af37;">0</div>
                    </div>
                    <div class="hud-card" style="border-top-color: #2b9348;">
                        <div class="hud-label" style="color: #2b9348;">📈 EFECTIVIDAD INSTITUCIONAL</div>
                        <div class="hud-value" style="color: #2b9348;">100%</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

            # Cápsula de despliegue informativo
            st.markdown("""
                <div class="contenedor-matriz">
                    <h4 style="color: #0d1b2a; font-weight: bold; margin-top: 0px; margin-bottom: 10px;">📊 Distribución del Rendimiento de Matrícula</h4>
                    <p style="color: #666; font-size: 13px; margin-bottom: 15px;">Métricas consolidadas listas para el procesamiento de promedios por asignaturas.</p>
                </div>
            """, unsafe_allow_html=True)
            
            # Aquí la app continuará desplegando tus gráficas de forma normal
            st.info("💡 **Sistema Listo:** Seleccione una evaluación en la central de escáner para comenzar a proyectar las gráficas estadísticas en tiempo real.")
        else:
            st.warning("⚠️ No se detectaron registros válidos para estructurar las analíticas.")
