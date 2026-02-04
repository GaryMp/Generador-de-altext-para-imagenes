"""
GaryText Pro - Interfaz Accesible WCAG 2.2 AA
Optimizado para NVDA y JAWS
"""

import streamlit as st
from PIL import Image
import io
import re
import piexif
import zipfile
import requests

# Configuración JSONbin.io para contadores
JSONBIN_BIN_ID = "6983d11b43b1c97be965ec3c"
JSONBIN_API_KEY = "$2a$10$6j4MIEVKRPTDxuwR3GRw2unUp8KZ3TbTvl/3psM5RA7nEpMZ8ALxO"

def obtener_contadores():
    """Obtiene los contadores actuales desde JSONbin"""
    try:
        url = f"https://api.jsonbin.io/v3/b/{JSONBIN_BIN_ID}/latest"
        headers = {"X-Master-Key": JSONBIN_API_KEY}
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            return response.json()["record"]
        return {"imagenes": 0, "visitas": 0}
    except:
        return {"imagenes": 0, "visitas": 0}

def actualizar_contadores(imagenes=0, visitas=0):
    """Incrementa los contadores en JSONbin"""
    try:
        datos = obtener_contadores()
        datos["imagenes"] = datos.get("imagenes", 0) + imagenes
        datos["visitas"] = datos.get("visitas", 0) + visitas

        url = f"https://api.jsonbin.io/v3/b/{JSONBIN_BIN_ID}"
        headers = {
            "Content-Type": "application/json",
            "X-Master-Key": JSONBIN_API_KEY
        }
        requests.put(url, json=datos, headers=headers, timeout=5)
        return datos
    except:
        return {"imagenes": 0, "visitas": 0}

st.set_page_config(
    page_title="GaryText Pro",
    page_icon="🖼️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# CSS WCAG 2.2 AA
st.markdown("""
<style>
    #MainMenu, footer, header {visibility: hidden;}

    /* Forzar tema claro */
    .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
        background-color: #ffffff !important;
    }

    [data-testid="stSidebar"] {
        background-color: #f8f9fa !important;
    }

    /* Opción 1: Borde superior degradado rasta */
    .stApp::before {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, #228B22 0%, #228B22 33%, #FFD700 33%, #FFD700 66%, #DC143C 66%, #DC143C 100%);
        z-index: 9999;
    }

    *:focus {
        outline: 3px solid #0056b3 !important;
        outline-offset: 3px !important;
    }

    body, .stMarkdown, p, span, label, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
        color: #1a1a1a !important;
    }

    .stButton > button {
        min-height: 44px;
        min-width: 44px;
        font-size: 1rem;
        padding: 0.75rem 1.5rem;
        background-color: #0056b3 !important;
        color: #ffffff !important;
        border: 2px solid #0056b3 !important;
    }

    .stButton > button:hover {
        background-color: #004494 !important;
    }

    .stButton > button:focus {
        box-shadow: 0 0 0 3px #ffffff, 0 0 0 6px #0056b3 !important;
    }

    .block-container {
        max-width: 600px;
        padding: 1rem;
    }

    /* Opción 3: Separadores con degradado rasta */
    hr {
        border: none !important;
        height: 2px !important;
        background: linear-gradient(90deg, #228B22 0%, #FFD700 50%, #DC143C 100%) !important;
        opacity: 0.6 !important;
        margin: 1rem 0 !important;
    }

    /* Radio buttons más accesibles */
    .stRadio > div {
        display: flex;
        flex-direction: column;
        gap: 8px;
    }

    .stRadio > div > label {
        min-height: 44px !important;
        display: flex !important;
        align-items: center !important;
        padding: 8px 12px !important;
        border: 2px solid #ccc !important;
        border-radius: 4px !important;
        cursor: pointer !important;
        background: #fff !important;
    }

    .stRadio > div > label:focus-within {
        border-color: #0056b3 !important;
        outline: 2px solid #0056b3 !important;
    }

    .stRadio > div > label > div:first-child {
        min-width: 24px !important;
        min-height: 24px !important;
    }

    /* Opción 2: Estilo para título con colores rasta */
    .rasta-title .gary-g { color: #228B22; }
    .rasta-title .gary-a { color: #FFD700; }
    .rasta-title .gary-r { color: #DC143C; }
    .rasta-title .gary-y { color: #228B22; }

    /* Opción 5: Footer con banda rasta */
    .rasta-footer {
        text-align: center;
        padding-top: 0.5rem;
        border-top: 3px solid;
        border-image: linear-gradient(90deg, #228B22 0%, #FFD700 50%, #DC143C 100%) 1;
    }
</style>
""", unsafe_allow_html=True)

# Cache del modelo
@st.cache_resource
def cargar_modelo():
    import torch
    from transformers import BlipProcessor, BlipForConditionalGeneration
    processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
    model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")
    return processor, model

def describir_imagen(imagen, processor, model):
    try:
        if imagen.mode != 'RGB':
            imagen = imagen.convert('RGB')
        inputs = processor(imagen, return_tensors="pt")
        out = model.generate(**inputs, max_length=80, num_beams=5, repetition_penalty=1.2)
        return processor.decode(out[0], skip_special_tokens=True)
    except:
        return "Error al procesar"

def traducir_al_espanol(texto):
    try:
        from deep_translator import GoogleTranslator
        return GoogleTranslator(source='en', target='es').translate(texto)
    except:
        return texto

def limpiar_nombre(texto):
    texto = texto.lower().replace(" ", "_")
    texto = re.sub(r'[^\w\s-]', '', texto)
    return texto[:60].strip("_")

def agregar_exif(imagen, texto_alt):
    try:
        exif_dict = {"0th": {}, "Exif": {}}
        texto_bytes = texto_alt.encode('utf-8')
        exif_dict["0th"][piexif.ImageIFD.ImageDescription] = texto_bytes
        exif_dict["Exif"][piexif.ExifIFD.UserComment] = texto_bytes
        return piexif.dump(exif_dict)
    except:
        return None

def imagen_a_bytes(imagen, exif_bytes=None):
    buffer = io.BytesIO()
    if exif_bytes:
        imagen.save(buffer, format="JPEG", exif=exif_bytes, quality=95)
    else:
        imagen.save(buffer, format="JPEG", quality=95)
    buffer.seek(0)
    return buffer

def anunciar_alerta(mensaje, mostrar_visual=False):
    """Genera una alerta para lectores de pantalla"""
    st.markdown(f"""
    <script>
        (function() {{
            var alertRegion = document.getElementById('sr-live-region');
            if (!alertRegion) {{
                alertRegion = document.createElement('div');
                alertRegion.id = 'sr-live-region';
                alertRegion.setAttribute('role', 'alert');
                alertRegion.setAttribute('aria-live', 'assertive');
                alertRegion.setAttribute('aria-atomic', 'true');
                alertRegion.style.position = 'absolute';
                alertRegion.style.left = '-10000px';
                alertRegion.style.width = '1px';
                alertRegion.style.height = '1px';
                alertRegion.style.overflow = 'hidden';
                document.body.appendChild(alertRegion);
            }}
            alertRegion.textContent = '';
            setTimeout(function() {{
                alertRegion.textContent = '{mensaje}';
            }}, 150);
        }})();
    </script>
    """, unsafe_allow_html=True)

    if mostrar_visual:
        st.success(mensaje)

# Estado inicial
if 'resultados' not in st.session_state:
    st.session_state.resultados = []
if 'archivos_previos' not in st.session_state:
    st.session_state.archivos_previos = set()
if 'uploader_key' not in st.session_state:
    st.session_state.uploader_key = 0
if 'mensaje_alerta' not in st.session_state:
    st.session_state.mensaje_alerta = ""
if 'mostrar_visual' not in st.session_state:
    st.session_state.mostrar_visual = False

# Funciones de callback
def marcar_descarga(nombre_archivo):
    st.session_state.mensaje_alerta = f"Descarga completada: {nombre_archivo}"
    st.session_state.mostrar_visual = False

def marcar_descarga_zip():
    st.session_state.mensaje_alerta = "Descarga completada: todas las imágenes en archivo ZIP."
    st.session_state.mostrar_visual = False

def limpiar_todo():
    st.session_state.resultados = []
    st.session_state.archivos_previos = set()
    st.session_state.uploader_key += 1
    st.session_state.mensaje_alerta = "Resultados eliminados. Puedes subir nuevas imágenes."
    st.session_state.mostrar_visual = True

def quitar_resultado(indice):
    st.session_state.resultados.pop(indice)
    if not st.session_state.resultados:
        st.session_state.archivos_previos = set()
        st.session_state.uploader_key += 1
        st.session_state.mensaje_alerta = "Resultados eliminados. Puedes subir nuevas imágenes."
        st.session_state.mostrar_visual = True

# ========== INTERFAZ ==========

st.markdown("""
<h1 tabindex="-1" class="rasta-title"><span class="gary-g">G</span><span class="gary-a">a</span><span class="gary-r">r</span><span class="gary-y">y</span>Text Pro</h1>
<p>Genera texto alternativo para tus imágenes con inteligencia artificial.</p>
""", unsafe_allow_html=True)

# Mostrar contadores
contadores = obtener_contadores()
st.markdown(f"""
<div style="text-align: center; padding: 0.5rem; background: linear-gradient(90deg, rgba(34,139,34,0.1), rgba(255,215,0,0.1), rgba(220,20,60,0.1)); border-radius: 8px; margin-bottom: 1rem;">
    <span style="margin-right: 1.5rem;">👁️ <strong id="contador-visitas">{contadores.get('visitas', 0):,}</strong> visitas</span>
    <span>📊 <strong id="contador-imagenes">{contadores.get('imagenes', 0):,}</strong> imágenes analizadas</span>
</div>

<script>
(function() {{
    const BIN_ID = "{JSONBIN_BIN_ID}";
    const API_KEY = "{JSONBIN_API_KEY}";
    const STORAGE_KEY = "garytext_visitado";

    // Verificar si ya visitó antes
    if (!localStorage.getItem(STORAGE_KEY)) {{
        // Marcar como visitado
        localStorage.setItem(STORAGE_KEY, Date.now().toString());

        // Incrementar contador en JSONbin
        fetch(`https://api.jsonbin.io/v3/b/${{BIN_ID}}/latest`, {{
            headers: {{ "X-Master-Key": API_KEY }}
        }})
        .then(res => res.json())
        .then(data => {{
            const datos = data.record;
            datos.visitas = (datos.visitas || 0) + 1;

            return fetch(`https://api.jsonbin.io/v3/b/${{BIN_ID}}`, {{
                method: "PUT",
                headers: {{
                    "Content-Type": "application/json",
                    "X-Master-Key": API_KEY
                }},
                body: JSON.stringify(datos)
            }});
        }})
        .then(res => res.json())
        .then(data => {{
            // Actualizar el contador en pantalla
            const el = document.getElementById("contador-visitas");
            if (el) el.textContent = data.record.visitas.toLocaleString();
        }})
        .catch(err => console.log("Error contador:", err));
    }}
}})();
</script>
""", unsafe_allow_html=True)

with st.expander("Instrucciones de uso"):
    st.markdown("""
**Pasos:**
1. Selecciona tus opciones
2. Sube imágenes con el botón Examinar
3. Presiona Generar con IA
4. Descarga los resultados

**Teclado:**
- Tab: siguiente elemento
- Shift+Tab: anterior
- Enter o Espacio: activar
- Flechas arriba/abajo: cambiar opciones
    """)

st.markdown("---")

# Mostrar alerta guardada después de rerun
if st.session_state.mensaje_alerta:
    mensaje_mostrar = st.session_state.mensaje_alerta
    visual = st.session_state.mostrar_visual
    st.session_state.mensaje_alerta = ""
    st.session_state.mostrar_visual = False
    anunciar_alerta(mensaje_mostrar, mostrar_visual=visual)

# OPCIONES
st.markdown("### Opciones")

# Opción de idioma usando selectbox (mejor accesibilidad con teclado)
st.markdown("**Idioma del texto alternativo:**")
idioma = st.selectbox(
    "Idioma del texto alternativo",
    options=["Español (traducir)", "Inglés (original)"],
    index=0,
    key="select_idioma",
    label_visibility="collapsed"
)
traducir = idioma == "Español (traducir)"

# Opción de metadatos
st.markdown("**Guardar en metadatos:**")
metadatos = st.selectbox(
    "Guardar en metadatos de imagen",
    options=["Sí, guardar en EXIF", "No, solo renombrar"],
    index=0,
    key="select_exif",
    label_visibility="collapsed"
)
guardar_exif = metadatos == "Sí, guardar en EXIF"

st.markdown("---")

# SUBIR IMÁGENES
st.markdown("### Subir imágenes")
st.markdown("Formatos: JPG, PNG, WEBP")

archivos = st.file_uploader(
    "Examinar archivos",
    type=["jpg", "jpeg", "png", "webp"],
    accept_multiple_files=True,
    key=f"uploader_{st.session_state.uploader_key}",
    label_visibility="collapsed"
)

# Detectar cambio en archivos
if archivos:
    nombres_actuales = {f.name for f in archivos}

    if nombres_actuales != st.session_state.archivos_previos:
        st.session_state.archivos_previos = nombres_actuales
        st.session_state.resultados = []

        cantidad = len(archivos)
        mensaje = f"{cantidad} {'imagen subida' if cantidad == 1 else 'imágenes subidas'}, {'lista' if cantidad == 1 else 'listas'} para procesar. Presiona el botón Generar con IA."
        anunciar_alerta(mensaje, mostrar_visual=True)

st.markdown("---")

# BOTÓN GENERAR
st.markdown("### Generar")

if archivos and not st.session_state.resultados:
    if st.button("Generar con IA", type="primary", use_container_width=True):

        # Contenedor para la alerta de procesamiento
        alerta_container = st.empty()
        alerta_container.markdown("""
        <div role="alert" aria-live="assertive" aria-atomic="true">
            Analizando imágenes, espera un momento.
        </div>
        """, unsafe_allow_html=True)

        try:
            with st.spinner("Cargando modelo..."):
                processor, model = cargar_modelo()

            barra = st.progress(0)

            for i, archivo in enumerate(archivos):
                barra.progress((i) / len(archivos))

                imagen = Image.open(archivo)
                if imagen.mode != 'RGB':
                    imagen = imagen.convert('RGB')

                descripcion = describir_imagen(imagen, processor, model)

                if traducir:
                    descripcion = traducir_al_espanol(descripcion)

                nombre_nuevo = f"{limpiar_nombre(descripcion)}.jpg"
                exif = agregar_exif(imagen, descripcion) if guardar_exif else None

                st.session_state.resultados.append({
                    "nombre": nombre_nuevo,
                    "descripcion": descripcion,
                    "imagen": imagen,
                    "exif": exif
                })

            barra.progress(100)
            barra.empty()
            alerta_container.empty()

            cantidad = len(st.session_state.resultados)
            actualizar_contadores(imagenes=cantidad)
            st.session_state.mensaje_alerta = f"Listo. {cantidad} {'imagen procesada' if cantidad == 1 else 'imágenes procesadas'}. Ya puedes descargar los resultados."
            st.session_state.mostrar_visual = True

            st.rerun()

        except Exception as e:
            alerta_container.empty()
            anunciar_alerta(f"Error: {str(e)}", mostrar_visual=True)

elif not archivos:
    st.markdown("Sube al menos una imagen para continuar.")

# RESULTADOS
if st.session_state.resultados:
    st.markdown("---")
    st.markdown("### Resultados")

    # Descarga ZIP si hay varias
    if len(st.session_state.resultados) > 1:
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
            for r in st.session_state.resultados:
                img_bytes = imagen_a_bytes(r['imagen'], r['exif'])
                zf.writestr(r['nombre'], img_bytes.getvalue())
        zip_buffer.seek(0)

        col1, col2 = st.columns([3, 1])
        with col1:
            st.download_button(
                "Descargar todo en ZIP",
                data=zip_buffer,
                file_name="garytext_imagenes.zip",
                mime="application/zip",
                use_container_width=True,
                on_click=marcar_descarga_zip
            )
        with col2:
            if st.button("Limpiar todo", use_container_width=True, on_click=limpiar_todo):
                st.rerun()

        st.markdown("---")

    # Resultados individuales
    for i, r in enumerate(st.session_state.resultados):
        st.markdown(f"**Imagen {i+1}:** {r['nombre']}")
        st.markdown(f"Texto: {r['descripcion']}")

        buffer = imagen_a_bytes(r['imagen'], r['exif'])

        col1, col2 = st.columns([3, 1])
        with col1:
            st.download_button(
                f"Descargar: {r['nombre']}",
                data=buffer,
                file_name=r['nombre'],
                mime="image/jpeg",
                key=f"dl_{i}",
                use_container_width=True,
                on_click=marcar_descarga,
                args=(r['nombre'],)
            )
        with col2:
            if st.button("Quitar", key=f"rm_{i}", use_container_width=True, on_click=quitar_resultado, args=(i,)):
                st.rerun()

        if i < len(st.session_state.resultados) - 1:
            st.markdown("---")

    # Botón limpiar si hay un solo resultado
    if len(st.session_state.resultados) == 1:
        st.markdown("---")
        if st.button("Limpiar y procesar nuevas imágenes", use_container_width=True, on_click=limpiar_todo):
            st.rerun()

# Footer
st.markdown("""
<div class="rasta-footer">
    <p style="margin-bottom: 0.5rem;">GaryText Pro v0.1 - Por Gary Dev</p>
    <p style="font-size: 0.9rem; color: #555; margin-bottom: 0.5rem;">
        Si te ha parecido útil esta aplicación, no dudes en donarme un café
    </p>
    <a href="https://ko-fi.com/garydev" target="_blank" rel="noopener noreferrer">
        <img src="https://storage.ko-fi.com/cdn/kofi2.png?v=3" alt="Donar un café en Ko-fi" style="height: 36px; border: 0;">
    </a>
</div>
""", unsafe_allow_html=True)
