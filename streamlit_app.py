"""
GaryText Pro - Interfaz Accesible WCAG 2.2 AA
Optimizado para NVDA y JAWS
"""

import streamlit as st
import streamlit.components.v1 as components
from PIL import Image
import io
import zipfile

from utils.gemini import GEMINI_API_KEY, describir_imagen
from utils.imagen import limpiar_nombre, agregar_exif, imagen_a_bytes
from utils.contadores import obtener_contadores, actualizar_contadores, JSONBIN_BIN_ID, JSONBIN_API_KEY
from utils.estilos import CSS_WCAG

st.set_page_config(
    page_title="GaryText Pro",
    page_icon="🖼️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# CSS WCAG 2.2 AA
st.markdown(CSS_WCAG, unsafe_allow_html=True)

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

def sincronizar_descripcion(indice):
    """Sincroniza el texto editado con los resultados almacenados"""
    nuevo_texto = st.session_state.get(f"txt_{indice}", "")
    if nuevo_texto and indice < len(st.session_state.resultados):
        st.session_state.resultados[indice]['descripcion'] = nuevo_texto

# ========== INTERFAZ ==========

st.markdown("""
<h1 tabindex="-1" class="rasta-title"><span class="gary-g">G</span><span class="gary-a">a</span><span class="gary-r">r</span><span class="gary-y">y</span>Text Pro</h1>
<p>Genera texto alternativo para tus imágenes con inteligencia artificial.</p>
""", unsafe_allow_html=True)

# Verificar API key
if not GEMINI_API_KEY:
    st.error("API key de Gemini no configurada. Configura GEMINI_API_KEY en los secrets de Streamlit.")

# Mostrar contadores
contadores = obtener_contadores()
st.markdown(f"""
<div style="text-align: center; padding: 0.5rem; background: linear-gradient(90deg, rgba(34,139,34,0.1), rgba(255,215,0,0.1), rgba(220,20,60,0.1)); border-radius: 8px; margin-bottom: 1rem;">
    <span style="margin-right: 1.5rem;">👁️ <strong>{contadores.get('visitas', 0):,}</strong> visitas</span>
    <span>📊 <strong>{contadores.get('imagenes', 0):,}</strong> imágenes analizadas</span>
</div>
""", unsafe_allow_html=True)

# Contador de visitas con JavaScript (se ejecuta en iframe)
components.html(f"""
<script>
(function() {{
    const BIN_ID = "{JSONBIN_BIN_ID}";
    const API_KEY = "{JSONBIN_API_KEY}";
    const STORAGE_KEY = "garytext_visitado";

    if (!localStorage.getItem(STORAGE_KEY)) {{
        localStorage.setItem(STORAGE_KEY, Date.now().toString());

        fetch("https://api.jsonbin.io/v3/b/" + BIN_ID + "/latest", {{
            headers: {{ "X-Master-Key": API_KEY }}
        }})
        .then(res => res.json())
        .then(data => {{
            const datos = data.record;
            datos.visitas = (datos.visitas || 0) + 1;

            return fetch("https://api.jsonbin.io/v3/b/" + BIN_ID, {{
                method: "PUT",
                headers: {{
                    "Content-Type": "application/json",
                    "X-Master-Key": API_KEY
                }},
                body: JSON.stringify(datos)
            }});
        }})
        .catch(err => console.log("Error contador:", err));
    }}
}})();
</script>
""", height=0)

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

# Opción de idioma
st.markdown("**Idioma del texto alternativo:**")
idioma = st.selectbox(
    "Idioma del texto alternativo",
    options=["Español", "Inglés"],
    index=0,
    key="select_idioma",
    label_visibility="collapsed"
)
usar_espanol = idioma == "Español"

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
            import time
            barra = st.progress(0)
            idioma_codigo = "es" if usar_espanol else "en"

            for i, archivo in enumerate(archivos):
                barra.progress((i) / len(archivos))

                # Delay para evitar rate limit (4s entre cada imagen)
                if i > 0:
                    time.sleep(4)
                else:
                    time.sleep(1)  # Pequeño delay inicial

                imagen = Image.open(archivo)
                if imagen.mode != 'RGB':
                    imagen = imagen.convert('RGB')

                resultado = describir_imagen(imagen, idioma_codigo)

                nombre_nuevo = f"{limpiar_nombre(resultado['nombre'])}.jpg"
                descripcion = resultado['descripcion']
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

    # Resultados individuales
    for i, r in enumerate(st.session_state.resultados):
        st.markdown(f"**Imagen {i+1}:** {r['nombre']}")

        texto_editado = st.text_area(
            f"Texto alternativo imagen {i+1}",
            value=r['descripcion'],
            key=f"txt_{i}",
            height=100,
            label_visibility="collapsed",
            on_change=sincronizar_descripcion,
            args=(i,)
        )

        # Regenerar EXIF con el texto editado (usar descripcion sincronizada)
        texto_para_descarga = st.session_state.resultados[i]['descripcion']
        exif_actual = agregar_exif(r['imagen'], texto_para_descarga) if guardar_exif else None
        buffer = imagen_a_bytes(r['imagen'], exif_actual)

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

    # Descarga ZIP y limpiar
    st.markdown("---")
    if len(st.session_state.resultados) > 1:
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
            for i, r in enumerate(st.session_state.resultados):
                texto_actual = st.session_state.get(f"txt_{i}", r['descripcion'])
                exif_zip = agregar_exif(r['imagen'], texto_actual) if guardar_exif else None
                img_bytes = imagen_a_bytes(r['imagen'], exif_zip)
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
    else:
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
