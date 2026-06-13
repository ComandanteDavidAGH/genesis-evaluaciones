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
    # 🎨 INYECCIÓN DE ALTA INGENIERÍA VISUAL (GÉNESIS MANAGEMENT HUD)
    st.markdown("""
        <style>
        /* 1. Encabezado Aeroespacial */
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
        
        /* 2. HUD - Indicadores Tácticos Flotantes (Copiado de tu Modelo Omega) */
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
        
        /* 3. Enmarcado Profesional de la Matriz */
        .contenedor-matriz {
            background-color: #ffffff;
            border-radius: 12px;
            border: 1px solid #e5e5e5;
            border-top: 4px solid #0d1b2a;
            padding: 20px;
            box-shadow: 0 8px 30px rgba(0,0,0,0.02);
            margin-top: 20px;
        }
        
        /* Ajuste de Bordes Quirúrgicos para la Tabla */
        div[data-testid="stDataFrame"] {
            border: 1px solid #e5e5e5 !important;
            border-radius: 8px !important;
            overflow: hidden !important;
        }
        </style>
    """, unsafe_allow_html=True)

    # Cabecera de Comando Principal
    st.markdown("<p class='titulo-genesis'>👥 Gestión de Estudiantes</p>", unsafe_allow_html=True)
    st.markdown("<p class='subtitulo-genesis'>Consola Central de Control de Matrícula e Infraestructura</p>", unsafe_allow_html=True)
    st.markdown("---")

    try:
        supabase = iniciar_conexion()
        # Jalamos la lista oficial con el espacio corregido del Correo
        resultado = supabase.table("data_estudiantes").select('ID_Estudiante, Nombre_Completo, Grado, Grupo, "Correo Institucional"').execute()
        estudiantes_base = resultado.data
    except Exception as e:
        st.error(f"🚨 Error de enlace seguro con el búnker de datos: {e}")
        return

    if estudiantes_base:
        # Procesamos la información de forma inteligente con Pandas
        df_unicos = pd.DataFrame(estudiantes_base).drop_duplicates(subset=["ID_Estudiante"])
        
        # 📊 TELEMETRÍA EN VIVO: Calculamos los datos reales del colegio
        total_matricula = len(df_unicos)
        total_grados = df_unicos["Grado"].nunique() if "Grado" in df_unicos.columns else 0
        total_grupos = df_unicos["Grupo"].nunique() if "Grupo" in df_unicos.columns else 0

        # =================================================================
        # 🎛️ EL REPLICA-HUD MINIMALISTA FLOTANTE (Fiel a tu modelo de referencia)
        # =================================================================
        st.markdown(f"""
            <div class="hud-container">
                <div class="hud-card" style="border-top-color: #0d1b2a;">
                    <div class="hud-label">👥 MATRÍCULA TOTAL</div>
                    <div class="hud-value" style="color: #0d1b2a;">{total_matricula}</div>
                </div>
                <div class="hud-card" style="border-top-color: #d4af37;">
                    <div class="hud-label" style="color: #bfa12a;">🏫 GRADOS ACTIVOS</div>
                    <div class="hud-value" style="color: #d4af37;">{total_grados}</div>
                </div>
                <div class="hud-card" style="border-top-color: #2b9348;">
                    <div class="hud-label" style="color: #2b9348;">🛡️ GRUPOS OPERATIVOS</div>
                    <div class="hud-value" style="color: #2b9348;">{total_grupos}</div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        # =================================================================
        # 📋 MATRIZ DE ESTUDIANTES ENMARCADA EN SU CRISTALERA
        # =================================================================
        st.markdown("""
            <div class="contenedor-matriz">
                <h4 style="color: #0d1b2a; font-weight: bold; margin-top: 0px; margin-bottom: 5px;">MATRIZ OFICIAL DE ESTUDIANTES MATRICULADOS</h4>
                <p style="color: #666; font-size: 13px; margin-bottom: 20px;">Registro confidencial sincronizado en tiempo real con el servidor de producción institucional.</p>
        """, unsafe_allow_html=True)

        # Ordenamos alfabéticamente para que se vea impecable
        df_ordenado = df_unicos.sort_values(by="Nombre_Completo")
        
        # Despliegue nítido dentro de la cápsula
        st.dataframe(
            df_ordenado[["ID_Estudiante", "Nombre_Completo", "Grado", "Grupo", "Correo Institucional"]],
            use_container_width=True,
            hide_index=True
        )
        st.markdown('</div>', unsafe_allow_html=True)
        
    else:
        st.warning("⚠️ Conexión establecida con éxito, pero la tabla 'data_estudiantes' se encuentra vacía.")
