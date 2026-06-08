import streamlit as st

# =================================================================
# 🏢 CONFIGURACIÓN ESTRUCTURAL DE LA PLATAFORMA ENTERPRISE
# =================================================================
st.set_page_config(
    page_title="Génesis Evaluaciones", 
    page_icon="🎯", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Importación de la estructura modular de la pirámide (Desde tu carpeta 'modulos')
try:
    from modulos import m0_gestion, m1_creador, m2_simulacro, m3_escaner, m4_dashboard
except ImportError as e:
    st.error(f"🚨 Falla de infraestructura de red: No se pudo cargar un módulo interno. Detalle: {e}")
    st.stop()

def main():
    # Estilización corporativa del menú lateral para aplastar a la competencia
    st.markdown("""
        <style>
        [data-testid="stSidebar"] { background-color: #0d1b2a; }
        [data-testid="stSidebar"] * { color: #ffffff; }
        div[data-testid="stSidebarNav"] { display: none; } /* Ocultar rutas por defecto */
        </style>
    """, unsafe_allow_html=True)

    with st.sidebar:
        # Tu logo de Flaticon corporativo original
        st.image("https://cdn-icons-png.flaticon.com/512/3285/3285816.png", width=100)
        st.markdown("## 🎯 GÉNESIS OMR")
        st.markdown("<p style='color: #d4af37; font-size:12px; margin-top:-10px;'>Plataforma de Evaluación Óptica v2.0</p>", unsafe_allow_html=True)
        st.markdown("---")
        
        # Panel de Comando Unificado
        menu = st.sidebar.radio(
            "📍 SELECCIONE EL MÓDULO:",
            [
                "👥 0. Gestión de Estudiantes",
                "⚙️ 1. Creador de Pruebas",
                "📱 2. Despliegue Digital (Alumnos)",
                "👁️ 3. Escáner OMR (Cámara)",
                "📊 4. Dashboard Analítico"
            ]
        )
        st.markdown("---")
        st.caption("Fase de Desarrollo - Modo Estable")

    # =================================================================
    # 🚀 ENRUTADOR MAESTRO DE TRÁFICO MULTI-MÓDULO
    # =================================================================
    if menu == "👥 0. Gestión de Estudiantes":
        m0_gestion.ejecutar()
        
    elif menu == "⚙️ 1. Creador de Pruebas":
        m1_creador.ejecutar()
        
    elif menu == "📱 2. Despliegue Digital (Alumnos)":
        m2_simulacro.ejecutar() 
        
    elif menu == "👁️ 3. Escáner OMR (Cámara)":
        m3_escaner.ejecutar()
        
    elif menu == "📊 4. Dashboard Analítico":
        m4_dashboard.ejecutar()

# ... (aquí termina tu enrutador con m4_dashboard.ejecutar()) ...

    # =================================================================
    # ☢️ MODO DESARROLLADOR (BOTÓN SECRETO DE SEMBRADO)
    # =================================================================
    st.sidebar.markdown("---")
    if st.sidebar.checkbox("🛠️ Activar Modo Dev"):
        st.sidebar.warning("Modo Admin Activo")
        if st.sidebar.button("🚀 INYECTAR DATOS DE PRUEBA", type="primary"):
            import random
            from supabase import create_client
            
            # Conexión local
            url = st.secrets["SUPABASE_URL"].replace('"', '').replace("'", "").strip()
            key = st.secrets["SUPABASE_KEY"].replace('"', '').replace("'", "").strip()
            supa_dev = create_client(url, key)
            
            materias_simulacro = [
                {"nombre": "Simulacro ICFES", "materia": "Lengua Castellana", "temas": ["Comprensión Lectora", "Gramática", "Literatura"]},
                {"nombre": "Prueba de Estado", "materia": "Matemáticas", "temas": ["Álgebra", "Geometría", "Trigonometría"]},
                {"nombre": "Evaluación Final", "materia": "Ciencias Sociales", "temas": ["Historia", "Geografía", "Democracia"]},
                {"nombre": "Test de Nivelación", "materia": "Inglés", "temas": ["Vocabulario", "Gramática", "Lectura"]}
            ]
            
            opciones = ["A", "B", "C", "D", "E"]
            nombres_estudiantes = ["Carlos Pérez (10A)", "María Gómez (10A)", "Luis Rodríguez (10B)", "Ana Martínez (10B)", "Jorge Hernández (11A)"]
            
            with st.spinner("Inyectando 20 registros masivos en Supabase..."):
                for mat in materias_simulacro:
                    llave = [{"Pregunta": f"Pregunta {i}", "Respuesta Correcta": random.choice(opciones), "Puntaje (Peso)": 1.0, "Tema": random.choice(mat["temas"])} for i in range(1, 21)]
                    res_prueba = supa_dev.table("pruebas_maestras").insert({"nombre": mat["nombre"], "materia": mat["materia"], "total_preguntas": 20, "puntaje_maximo": 20.0, "llave_maestra": llave}).execute()
                    id_prueba = res_prueba.data[0]["id_prueba"]
                    
                    for est in nombres_estudiantes:
                        respuestas = {}
                        aciertos = 0
                        for item in llave:
                            if random.random() < 0.70:
                                resp = item["Respuesta Correcta"]
                                aciertos += 1
                            else:
                                resp = random.choice([opt for opt in opciones if opt != item["Respuesta Correcta"]])
                            respuestas[item["Pregunta"]] = resp
                        
                        supa_dev.table("respuestas_estudiantes").insert({
                            "id_prueba": id_prueba, "nombre_prueba": mat["nombre"], "estudiante": est,
                            "respuestas_json": respuestas, "puntaje_obtenido": float(aciertos), "puntaje_maximo": 20.0, "porcentaje": (aciertos/20)*100
                        }).execute()
                        
            st.sidebar.success("✅ Base de datos poblada. ¡Ve al Dashboard!")

if __name__ == "__main__":
    main()
