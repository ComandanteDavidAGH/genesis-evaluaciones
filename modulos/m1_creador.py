import streamlit as st
import os

def ejecutar():
    # 💥 DETONADOR DE VERDAD CONTRA EL CACHÉ
    st.markdown("<h1 style='color: #d90429; text-align: center;'>🚨 ¡MÁXIMA ALERTA: CEBO TRAMPA DETONADO! 🚨</h1>", unsafe_allow_html=True)
    st.error("Si estás viendo este letrero ROJO GIGANTE, significa que el servidor SÍ está leyendo tus cambios en GitHub hoy domingo.")
    
    # 🕵️‍♂️ TELEMETRÍA DE RUTAS REALES
    st.markdown("### 🛰️ Telemetría del Servidor en Vivo")
    st.info(f"📁 Ruta exacta del archivo que se está ejecutando: `{__file__}`")
    
    # 📄 PRUEBA REINA: Intentar leer lo que el disco duro tiene escrito en este instante
    try:
        with open(__file__, "r", encoding="utf-8") as f:
            primeras_lineas = f.readlines()[:6]
        st.success(f"📝 Primeras líneas reales escritas en este archivo dentro del servidor:\n`{primeras_lineas}`")
    except Exception as e:
        st.code(f"Fallo crítico al intentar leer el disco duro: {e}")

    st.markdown("---")
    st.warning("⚠️ El resto de la aplicación ha sido congelada intencionalmente por el cebo de diagnóstico.")
