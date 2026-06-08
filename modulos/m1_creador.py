import streamlit as st
import uuid
from supabase import create_client, Client

# =================================================================
# 🔌 CONEXIÓN AL CENTRO DE DATOS
# =================================================================
@st.cache_resource
def iniciar_conexion():
    url = st.secrets["SUPABASE_URL"].replace('"', '').replace("'", "").strip()
    key = st.secrets["SUPABASE_KEY"].replace('"', '').replace("'", "").strip()
    return create_client(url, key)

def generar_hoja_imprimible_html(nombre_prueba, materia, num_preguntas):
    burbujas_html = ""
    for i in range(num_preguntas):
        burbujas_html += f"""
        <div class="fila-omr">
            <span class="num-preg font-weight-bold">P{i+1:02d}</span>
            <div class="circulo">A</div>
            <div class="circulo">B</div>
            <div class="circulo">C</div>
            <div class="circulo">D</div>
            <div class="circulo">E</div>
        </div>
        """
    
    id_columnas_html = ""
    for col in range(3):
        filas_digitos = "".join([f'<div class="circulo-id">{d}</div>' for d in range(10)])
        id_columnas_html += f"""
        <div class="columna-id-omr">
            <div class="label-id">D{col+1}</div>
            {filas_digitos}
        </div>
        """

    html_completo = f"""
    <div class="hoja-omr-impresa">
        <div class="anclaje sup-izq"></div>
        <div class="anclaje sup-der"></div>
        <div class="anclaje inf-izq"></div>
        <div class="anclaje inf-der"></div>
        
        <div class="encabezado-omr">
            <h2>🎯 GÉNESIS OMR - HOJA DE RESPUESTAS</h2>
            <p><strong>Evaluación:</strong> {nombre_prueba} | <strong>Área:</strong> {materia}</p>
            <hr style="border: 0; border-top: 1px solid #000; margin: 10px 0;">
            <div style="margin-top: 10px; text-align: left;">
                <span style="display:inline-block; width:60%; border-bottom:1px solid #000; padding-bottom:5px;"><strong>Estudiante:</strong> </span>
                <span style="display:inline-block; width:35%; border-bottom:1px solid #000; padding-bottom:5px; margin-left:4%;"><strong>Fecha:</strong> ____/____/______</span>
            </div>
        </div>

        <div class="cuerpo-omr">
            <div class="bloque-id-container">
                <h4 style="text-align:center; margin: 0 0 5px 0; font-size:12px;">🆔 CÓDIGO ESTUDIANTE</h4>
                <div class="grilla-id-omr">
                    {id_columnas_html}
                </div>
            </div>

            <div class="bloque-respuestas-container">
                <h4 style="text-align:center; margin: 0 0 10px 0; font-size:12px;">📝 RESPUESTAS</h4>
                <div class="contenedor-filas">
                    {burbujas_html}
                </div>
            </div>
        </div>
    </div>

    <style>
        .hoja-omr-impresa {{ 
            position: relative; 
            background-color: #ffffff; 
            color: #000000; 
            padding: 40px; 
            font-family: 'Arial', sans-serif; 
            border: 2px solid #000000; 
            border-radius: 8px; 
            margin: 20px auto; 
            max-width: 650px;
            box-shadow: 0px 4px 10px rgba(0,0,0,0.05);
        }}
        .anclaje {{ position: absolute; width: 20px; height: 20px; background-color: #000000; }}
        .sup-izq {{ top: 15px; left: 15px; }} .sup-der {{ top: 15px; right: 15px; }} .inf-izq {{ bottom: 15px; left: 15px; }} .inf-der {{ bottom: 15px; right: 15px; }}
        .encabezado-omr h2 {{ margin: 0; font-size: 18px; color: #0d1b2a; text-align: center; font-family: 'Arial Black', sans-serif; }}
        .encabezado-omr p {{ margin: 5px 0 0 0; font-size: 12px; text-align: center; color: #333; }}
        .cuerpo-omr {{ display: flex; margin-top: 25px; justify-content: space-between; }}
        .bloque-id-container {{ width: 32%; border: 1.5px dashed #000; padding: 10px; border-radius: 5px; }}
        .grilla-id-omr {{ display: flex; justify-content: space-around; }}
        .columna-id-omr {{ display: flex; flex-direction: column; align-items: center; }}
        .label-id {{ font-size: 10px; font-weight: bold; margin-bottom: 4px; }}
        .circulo-id {{ width: 18px; height: 18px; border: 1.5px solid #000; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 9px; margin: 2px 0; font-weight: bold; }}
        .bloque-respuestas-container {{ width: 64%; border: 1.5px dashed #000; padding: 10px; border-radius: 5px; }}
        .contenedor-filas {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 5px 15px; }}
        .fila-omr {{ display: flex; align-items: center; justify-content: space-between; padding: 2px 0; }}
        .num-preg {{ font-size: 11px; width: 25px; text-align: left; }}
        .circulo {{ width: 18px; height: 18px; border: 1.5px solid #000; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 9px; font-weight: bold; }}
    </style>
    """
    return html_completo

def ejecutar():
    st.markdown("<h1 style='color: #0d1b2a;'>⚙️ Centro de Comando: Diseñador de Pruebas</h1>", unsafe_allow_html=True)
    st.caption("Estructuración de plantillas maestras y alineamiento por competencias temáticas.")
    
    try:
        supabase: Client = iniciar_conexion()
    except Exception:
        st.error("⚠️ Falla crítica en la línea de suministro de datos.")
        return

    bloque_creacion, bloque_impresion = st.tabs(["🆕 Crear Nueva Plantilla", "🖨️ Fábrica de Hojas Imprimibles (PDF)"])

    with bloque_creacion:
        st.markdown("### 📝 Datos de la Matriz")
        c1, c2 = st.columns(2)
        with c1: nombre_prueba = st.text_input("Nombre de la Prueba:", placeholder="Ej: Parcial de Competencias")
        with c2: materia = st.text_input("Asignatura / Área:", placeholder="Ej: Ciencias Sociales")
        
        num_preguntas = st.slider("Cantidad de objetivos a evaluar (Preguntas):", min_value=1, max_value=30, value=10)
        puntaje_maximo = st.number_input("Puntaje Máximo de la prueba:", min_value=1.0, max_value=100.0, value=5.0, step=1.0)
        
        st.markdown("---")
        st.markdown("### 🔑 Configuración de la Llave Maestra y Temas Diagnósticos")
        
        peso_equitativo = round(puntaje_maximo / num_preguntas, 2)
        st.info(f"⚖️ Cada pregunta aportará **{peso_equitativo}** puntos a la nota definitiva.")
        
        llave_maestra_lista = []
        for i in range(num_preguntas):
            st.markdown(f"**📍 Ítem N° {i+1}**")
            cx1, cx2 = st.columns([1, 3])
            with cx1:
                opcion_correcta = st.selectbox(f"Opción Correcta", ["A", "B", "C", "D", "E"], key=f"p_{i}", label_visibility="collapsed")
            with cx2:
                tema_pregunta = st.text_input(f"Tema / Componente Evaluado", value="Conceptos Clave", key=f"t_{i}", placeholder="Ej: Comprensión Lectora, Geometría", label_visibility="collapsed")
            
            llave_maestra_lista.append({
                "Pregunta": f"Pregunta {i+1}",
                "Respuesta Correcta": opcion_correcta,
                "Puntaje (Peso)": peso_equitativo,
                "Tema": tema_pregunta.strip() if tema_pregunta.strip() else "General"
            })
            st.markdown("<div style='margin-bottom:10px;'></div>", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🚀 TRANSMITIR Y ASEGURAR PLANTILLA EN EL BÚNKER", use_container_width=True):
            if not nombre_prueba or not materia:
                st.error("⚠️ Operación abortada: Debe asignar Nombre y Asignatura a la plantilla.")
                return
                
            id_unico_prueba = str(uuid.uuid4())
            paquete_datos = {
                "id_prueba": id_unico_prueba,
                "nombre": nombre_prueba,
                "materia": materia,
                "total_preguntas": num_preguntas,
                "puntaje_maximo": puntaje_maximo,
                "lock": False,
                "llave_maestra": llave_maestra_lista
            }
            
            try:
                supabase.table("pruebas_maestras").insert(paquete_datos).execute()
                st.balloons()
                st.success(f"¡CONFIRMADO! La plantilla '{nombre_prueba}' con mapeo de temas ha sido asegurada.")
            except Exception as e:
                st.error(f"💥 Falla en la inyección de datos: {e}")

    with bloque_impresion:
        st.markdown("### 🖨️ Impresor de Hojas de Burbujas")
        st.write("Selecciona una plantilla para generar la hoja física adaptada. Luego presiona **Ctrl + P**.")
        try:
            listado = supabase.table("pruebas_maestras").select("*").execute().data
        except Exception:
            st.error("Error al extraer plantillas.")
            return

        if not listado:
            st.info("📭 No hay plantillas creadas todavía.")
            return

        diccionario_hojas = {f"{p['nombre']} - {p['materia']}": p for p in listado}
        seleccionada = st.selectbox("Elige la prueba a imprimir:", list(diccionario_hojas.keys()))
        
        datos_hoja = diccionario_hojas[seleccionada]
        html_hoja = generar_hoja_imprimible_html(datos_hoja["nombre"], datos_hoja["materia"], datos_hoja["total_preguntas"])
        
        # =====================================================================
        # 🛡️ LA CAPA FANTASMA V2: Bisturí CSS (Oculta botones, salva la hoja)
        # =====================================================================
        st.markdown("""
        <style>
        @media print {
            /* 1. Ocultar la barra lateral, el header superior y el pie de página */
            section[data-testid="stSidebar"], 
            header[data-testid="stHeader"], 
            footer {
                display: none !important;
            }
            
            /* 2. Ocultar los botones de las pestañas, selectores y textos descriptivos */
            div[data-testid="stTabs"] > div[role="tablist"],
            div[data-testid="stSelectbox"],
            div[data-testid="stMarkdownContainer"] > h3,
            div[data-testid="stMarkdownContainer"] > p {
                display: none !important;
            }
            
            /* 3. Evitar que la hoja quede apretada (forzar ancho completo) */
            .main .block-container {
                padding: 0 !important;
                margin: 0 !important;
                max-width: 100% !important;
            }

            /* 4. Quitar la sombra de la hoja en el papel impreso */
            .hoja-omr-impresa {
                box-shadow: none !important;
                border: none !important;
            }
        }
        </style>
        """, unsafe_allow_html=True)

        st.markdown("---")
        # Inyectamos la hoja comprimiendo los saltos de línea para que Streamlit la dibuje bien
        html_puro = html_hoja.replace('\n', '')
        st.markdown(f'<div class="bunker-impresion-limpia">{html_puro}</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    ejecutar()
