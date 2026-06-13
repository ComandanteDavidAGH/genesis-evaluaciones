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
    # 🎨 INYECCIÓN ESTÉTICA PREMIUM (Identidad Visual GÉNESIS)
    st.markdown("""
        <style>
        /* 1. Títulos Principales en Azul de Mando y Oro */
        .titulo-genesis {
            color: #0d1b2a;
            font-family: 'Arial Black', sans-serif;
            font-size: 32px;
            margin-bottom: 0px;
        }
        .subtitulo-genesis {
            color: #d4af37;
            font-weight: bold;
            font-size: 14px;
            margin-top: -5px;
            letter-spacing: 1px;
            text-transform: uppercase;
        }
        
        /* 2. Tarjeta Contenedora de la Matrícula */
        .tarjeta-tabla {
            background-color: #f8f9fa;
            border-left: 5px solid #0d1b2a;
            padding: 20px;
            border-radius: 4px 12px 12px 4px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.02);
            margin-top: 20px;
        }
        
        /* 3. Casilla de Telemetría para el Conteo de Alumnos */
        .casilla-conteo {
            background-color: #ffffff;
            border-radius: 12px;
            padding: 15px 20px;
            text-align: center;
            box-shadow: 0 6px 15px rgba(0, 0, 0, 0.06);
            border: 2.5px solid #d4af37;
            max-width: 280px;
            margin-bottom: 20px;
            transition: transform 0.2s;
        }
        .casilla-conteo:hover {
            transform: translateY(-2px);
        }
        </style>
    """, unsafe_allow_html=True)

    # Cabecera oficial unificada
    st.markdown("<p class='titulo-genesis'>👥 Gestión de Estudiantes</p>", unsafe_allow_html=True)
    st.markdown("<p class='subtitulo-genesis'>Control Global de Matrícula Escolar en Vivo</p>", unsafe_allow_html=True)
    st.markdown("---")

    try:
        supabase = iniciar_conexion()
        # Jalamos la lista oficial con el espacio corregido del Correo
        resultado = supabase.table("data_estudiantes").select('ID_Estudiante, Nombre_Completo, Grado, Grupo, "Correo Institucional"').execute()
        estudiantes_base = resultado.data
    except Exception as e:
        st.error(f"🚨 Error de enlace seguro: {e}")
        return

    if estudiantes_base:
        df_unicos = pd.DataFrame(estudiantes_base).drop_duplicates(subset=["ID_Estudiante"])
        total_matriculados = len(df_unicos)
        
        # =================================================================
        # 🎛️ INDICADOR TÁCTIL DE MATRÍCULA (Estilo Mejorado a Omega)
        # =================================================================
        st.markdown(f"""
            <div class="casilla-conteo">
                <div style="font-size: 11px; font-weight: 800; color: #bfa12a; letter-spacing: 1px; text-transform: uppercase;">📊 TOTAL MATRÍCULA OFICIAL</div>
                <div style="font-size: 38px; font-family: 'Arial Black', sans-serif; font-weight: 900; color: #0d1b2a; line-height: 1.1; margin-top: 4px;">{total_matriculados}</div>
            </div>
        """, unsafe_allow_html=True)

        # =================================================================
        # 📋 MARCO DE LA TABLA INSTITUCIONAL
        # =================================================================
        st.markdown("""
            <div class="tarjeta-tabla">
                <h4 style="color: #0d1b2a; font-weight: bold; margin-top: 0px; margin-bottom: 10px;">📋 Registro de Alumnos Activos</h4>
                <p style="color: #666; font-size: 13px; margin-bottom: 15px;">Listado oficial sincronizado directamente desde el búnker de datos de producción.</p>
            </div>
        """, unsafe_allow_html=True)
        
        # Despliegue limpio de los datos ordenados por nombre
        df_ordenado = df_unicos.sort_values(by="Nombre_Completo")
        st.dataframe(
            df_ordenado[["ID_Estudiante", "Nombre_Completo", "Grado", "Grupo", "Correo Institucional"]],
            use_container_width=True,
            hide_index=True
        )
    else:
        st.warning("⚠️ La tabla 'data_estudiantes' se enlazó con éxito pero no contiene registros en su interior.")
