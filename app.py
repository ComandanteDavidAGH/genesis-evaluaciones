import streamlit as st
import sys

st.set_page_config(page_title="Radar de Diagnóstico GÉNESIS", page_icon="🪤", layout="wide")

st.markdown("<h1 style='color: #d4af37;'>🪤 CEBO TRAMPA: Radar de Infraestructura</h1>", unsafe_allow_html=True)
st.write("Comandante, dejamos de disparar a ciegas. Este script va a aislar el fallo real en vivo.")
st.markdown("---")

# =================================================================
# 🔍 PRUEBA 1: CAZADOR DE CARACTERES FANTASMA (ASCII/HEX TELEMETRÍA)
# =================================================================
st.subheader("🕵️‍♂️ 1. Análisis de Micro-Espacios Invisibles en Cabecera")
try:
    with open(__file__, "r", encoding="utf-8") as f:
        lineas = f.readlines()
    
    analisis = []
    for i, linea in enumerate(lineas[:6]):
        # Representación cruda para ver si hay caracteres raros como \xa0
        analisis.append({"Línea": i+1, "Contenido Real": repr(linea), "Largo": len(linea)})
    st.table(analisis)
except Exception as e:
    st.error(f"No se pudo auditar el archivo a nivel de bytes: {e}")

st.markdown("---")

# =================================================================
# 📦 PRUEBA 2: EMBOSCADA DE IMPORTACIÓN AISLADA
# =================================================================
st.subheader("⚡ 2. Escáner de Módulos Internos (Aislamiento de Culpables)")
st.caption("Estamos importando cada archivo en un búnker cerrado. Si alguno tiene un IndentationError por dentro, la trampa lo va a capturar aquí abajo:")

modulos_a_probar = [
    ("👥 Módulo 0: Gestión de Estudiantes", "modulos.m0_gestion"),
    ("⚙️ Módulo 1: Creador de Pruebas", "modulos.m1_creador"),
    ("📱 Módulo 2: Despliegue Digital (Alumnos)", "modulos.m2_simulacro"),
    ("👁️ Módulo 3: Escáner OMR (Cámara)", "modulos.m3_escaner"),
    ("📊 Módulo 4: Dashboard Analítico", "modulos.m4_dashboard")
]

for nombre, ruta in modulos_a_probar:
    try:
        # Importación dinámica en tiempo de ejecución para evitar el colapso del compilador
        __import__(ruta)
        st.success(f"{nombre}: 🟢 TOTALMENTE LIMPIO. Listo para operar.")
    except IndentationError as ie:
        st.error(f"{nombre}: ❌ ¡CAPTURADO EL ENEMIGO! El error de sangría está DENTRO de este archivo.")
        st.exception(ie)
    except Exception as ex:
        # Es normal que salte esto si faltan variables, lo importante es que no sea un IndentationError
        st.warning(f"{nombre}: 🟡 Estructura de sangría OK (Detuvo la carga por lógica interna): {ex}")
