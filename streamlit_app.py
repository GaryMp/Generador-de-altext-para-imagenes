"""
GaryText Pro - Interfaz Accesible WCAG 2.2 AA
Optimizado para NVDA y JAWS
"""

import streamlit as st
import streamlit.components.v1 as components
from PIL import Image
import io
import zipfile
import time

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

# Inyectar lang="es" para screen readers (WCAG 3.1.1)
components.html("""
<script>
(function() {
    try {
        var root = window.parent.document.documentElement;
        root.setAttribute('lang', 'es');
    } catch(e) {}
    try { if (window.frameElement) {
        window.frameElement.setAttribute('aria-hidden', 'true');
        window.frameElement.tabIndex = -1;
        window.frameElement.title = '';
        window.frameElement.style.display = 'none';
    }} catch(e) {}
})();
</script>
""", height=0)

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
if 'error_procesamiento' not in st.session_state:
    st.session_state.error_procesamiento = False
if 'procesando_indice' not in st.session_state:
    st.session_state.procesando_indice = -1
if 'foco_resultados' not in st.session_state:
    st.session_state.foco_resultados = False
if 'foco_subir' not in st.session_state:
    st.session_state.foco_subir = False

# Funciones de callback
def marcar_descarga(nombre_archivo):
    st.session_state.mensaje_alerta = f"Descarga completada: {nombre_archivo}"
    st.session_state.mostrar_visual = True

def marcar_descarga_zip():
    st.session_state.mensaje_alerta = "Descarga completada: todas las imágenes en archivo ZIP."
    st.session_state.mostrar_visual = True

def limpiar_todo():
    st.session_state.resultados = []
    st.session_state.archivos_previos = set()
    st.session_state.uploader_key += 1
    st.session_state.error_procesamiento = False
    st.session_state.procesando_indice = -1
    st.session_state.mensaje_alerta = "Resultados eliminados. Puedes subir nuevas imágenes."
    st.session_state.mostrar_visual = True
    st.session_state.foco_subir = True

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
<h1 tabindex="-1" class="rasta-title">
    <span class="sr-only">GaryText Pro</span>
    <span aria-hidden="true"><span class="gary-g">G</span><span class="gary-a">a</span><span class="gary-r">r</span><span class="gary-y">y</span>Text Pro</span>
</h1>
<p>Genera texto alternativo para tus imágenes con inteligencia artificial.</p>
""", unsafe_allow_html=True)

# Verificar API key
if not GEMINI_API_KEY:
    st.error("API key de Gemini no configurada. Configura GEMINI_API_KEY en los secrets de Streamlit.")

# Obtener contadores (se muestran en el footer)
contadores = obtener_contadores()

# Mostrar alerta guardada después de rerun
if st.session_state.mensaje_alerta:
    mensaje_mostrar = st.session_state.mensaje_alerta
    visual = st.session_state.mostrar_visual
    st.session_state.mensaje_alerta = ""
    st.session_state.mostrar_visual = False
    if visual:
        st.success(mensaje_mostrar)


# OPCIONES AVANZADAS (colapsadas por defecto)
with st.expander("Opciones avanzadas"):
    idioma = st.selectbox(
        "Idioma del texto alternativo",
        options=["Español", "Inglés"],
        index=0,
        key="select_idioma"
    )
    metadatos = st.selectbox(
        "Guardar en metadatos de imagen",
        options=["Sí, guardar en EXIF", "No, solo renombrar"],
        index=0,
        key="select_exif"
    )
usar_espanol = idioma == "Español"
guardar_exif = metadatos == "Sí, guardar en EXIF"

# CATEGORÍA DE ANÁLISIS
if 'categoria_elegida' not in st.session_state:
    st.session_state.categoria_elegida = "General"
if 'categoria_cambio' not in st.session_state:
    st.session_state.categoria_cambio = False

def _seleccionar_cat(cat):
    st.session_state.categoria_elegida = cat
    st.session_state.categoria_cambio = True

cat_actual = st.session_state.categoria_elegida
opciones_cat = ["General", "Personas", "Vestuario", "Paisajes"]
with st.expander(f"Categoría de análisis: {cat_actual}"):
    for cat in opciones_cat:
        es_seleccionada = cat == cat_actual
        st.button(
            f"✓ {cat}" if es_seleccionada else cat,
            on_click=_seleccionar_cat,
            args=(cat,),
            use_container_width=True,
            key=f"btn_cat_{cat.lower()}",
            type="primary" if es_seleccionada else "secondary"
        )
categoria_codigo = cat_actual.lower()

# Cerrar expander y mover foco después de seleccionar categoría
if st.session_state.categoria_cambio:
    st.session_state.categoria_cambio = False
    components.html(f"""
    <script>
    // {time.time()}
    (function() {{
        try {{ if (window.frameElement) {{
            window.frameElement.setAttribute('aria-hidden', 'true');
            window.frameElement.tabIndex = -1;
            window.frameElement.style.display = 'none';
        }} }} catch(e) {{}}
        function cerrarYEnfocar() {{
            var doc = window.parent.document;
            var expanders = doc.querySelectorAll('[data-testid="stExpander"]');
            for (var i = 0; i < expanders.length; i++) {{
                var summary = expanders[i].querySelector('summary');
                if (summary && summary.textContent.indexOf('Categoría de análisis') !== -1) {{
                    var details = expanders[i].querySelector('details');
                    if (details) details.removeAttribute('open');
                    setTimeout(function() {{ summary.focus(); }}, 100);
                    break;
                }}
            }}
        }}
        setTimeout(cerrarYEnfocar, 300);
    }})();
    </script>
    """, height=0)

# SUBIR IMÁGENES
st.markdown('<h2 id="subir-imagenes" tabindex="-1">Subir imágenes</h2>', unsafe_allow_html=True)
st.markdown("Formatos: JPG, PNG, WEBP")

# Mover foco a "Subir imágenes" después de limpiar resultados
if st.session_state.foco_subir:
    st.session_state.foco_subir = False
    components.html(f"""
    <script>
    // {time.time()}
    (function() {{
        try {{ if (window.frameElement) {{
            window.frameElement.setAttribute('aria-hidden', 'true');
            window.frameElement.tabIndex = -1;
            window.frameElement.style.display = 'none';
        }} }} catch(e) {{}}
        setTimeout(function() {{
            var doc = window.parent.document;
            var expanders = doc.querySelectorAll('[data-testid="stExpander"] summary');
            for (var i = 0; i < expanders.length; i++) {{
                if (expanders[i].textContent.indexOf('Categoría de análisis') !== -1) {{
                    expanders[i].blur();
                    setTimeout(function() {{ expanders[i].focus(); }}, 200);
                    break;
                }}
            }}
        }}, 1900);
    }})();
    </script>
    """, height=0)

archivos = st.file_uploader(
    "Examinar archivos",
    type=["jpg", "jpeg", "png", "webp"],
    accept_multiple_files=True,
    key=f"uploader_{st.session_state.uploader_key}",
    label_visibility="collapsed"
)

# Detectar cambio en archivos → iniciar procesamiento
if archivos:
    nombres_actuales = {f.name for f in archivos}

    if nombres_actuales != st.session_state.archivos_previos:
        st.session_state.archivos_previos = nombres_actuales
        st.session_state.resultados = []
        st.session_state.error_procesamiento = False
        st.session_state.procesando_indice = 0
        total = len(archivos)
        st.session_state.mensaje_alerta = f"Analizando {total} {'imagen' if total == 1 else 'imágenes'}, espera un momento."
        st.session_state.mostrar_visual = True
        st.rerun()

# PROCESAR UNA IMAGEN A LA VEZ (con feedback NVDA entre cada una)
if archivos and st.session_state.procesando_indice >= 0:
    # Animación rasta durante procesamiento
    st.markdown('<style>.stApp::before{height:6px;background:repeating-linear-gradient(90deg,#228B22 0%,#FFD700 16%,#DC143C 33%,#228B22 50%);background-size:200% 100%;animation:rasta-slide 1.5s linear infinite;}</style>', unsafe_allow_html=True)

    idx = st.session_state.procesando_indice
    total = len(archivos)

    if idx < total and not st.session_state.error_procesamiento:
        # Barra de progreso visual
        st.progress(idx / total, text=f"Procesando imagen {idx + 1} de {total}...")

        try:
            # Delay para rate limit
            time.sleep(1)

            idioma_codigo = "es" if usar_espanol else "en"
            archivo = archivos[idx]
            imagen = Image.open(archivo)
            if imagen.mode != 'RGB':
                imagen = imagen.convert('RGB')

            resultado = describir_imagen(imagen, idioma_codigo, categoria_codigo)

            nombre_nuevo = f"{limpiar_nombre(resultado['nombre'])}.jpg"
            descripcion = resultado['descripcion']
            exif = agregar_exif(imagen, descripcion) if guardar_exif else None

            st.session_state.resultados.append({
                "nombre": nombre_nuevo,
                "descripcion": descripcion,
                "imagen": imagen,
                "exif": exif
            })

            st.session_state.procesando_indice = idx + 1

            if idx + 1 < total:
                restantes = total - (idx + 1)
                if restantes == 1:
                    st.session_state.mensaje_alerta = f"Imagen {idx+1} de {total} procesada. Falta solo una más."
                else:
                    st.session_state.mensaje_alerta = f"Imagen {idx+1} de {total} procesada. Faltan {restantes} más."
                st.session_state.mostrar_visual = True
            else:
                # Todas procesadas
                st.session_state.procesando_indice = -1
                actualizar_contadores(imagenes=total)
                st.session_state.mensaje_alerta = f"Listo. {total} {'imagen procesada' if total == 1 else 'imágenes procesadas'}. Ya puedes descargar los resultados. Recuerda, la IA puede cometer errores, no te fíes completamente de los análisis."
                st.session_state.mostrar_visual = True
                st.session_state.foco_resultados = True

            st.rerun()

        except Exception as e:
            st.session_state.error_procesamiento = True
            st.session_state.procesando_indice = -1
            st.error(f"Error al procesar: {str(e)}")

    elif st.session_state.error_procesamiento:
        st.error("Hubo un error al procesar las imágenes.")
        if st.button("Reintentar", type="primary", use_container_width=True):
            st.session_state.error_procesamiento = False
            st.session_state.procesando_indice = 0
            st.session_state.resultados = []
            st.rerun()

# RESULTADOS (solo cuando terminó el procesamiento)
if st.session_state.resultados and st.session_state.procesando_indice < 0:
    st.markdown("---")
    st.markdown('<h2 id="resultados" tabindex="-1">Resultados</h2>', unsafe_allow_html=True)

    # Mover foco al encabezado Resultados al terminar el procesamiento
    if st.session_state.foco_resultados:
        st.session_state.foco_resultados = False
        components.html(f"""
        <script>
        // {time.time()}
        (function() {{
            try {{ if (window.frameElement) {{
                window.frameElement.setAttribute('aria-hidden', 'true');
                window.frameElement.tabIndex = -1;
                window.frameElement.style.display = 'none';
            }} }} catch(e) {{}}
            setTimeout(function() {{
                var h2 = window.parent.document.getElementById('resultados');
                if (h2) {{
                    h2.blur();
                    setTimeout(function() {{ h2.focus(); }}, 200);
                }}
            }}, 4900);
        }})();
        </script>
        """, height=0)

    # Resultados individuales
    for i, r in enumerate(st.session_state.resultados):
        col_thumb, col_info = st.columns([1, 3])
        with col_thumb:
            st.image(r['imagen'], width=100, caption=f"Imagen {i+1}")
        with col_info:
            st.markdown(f"**{r['nombre']}**")
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
            nombre_corto = r['nombre'][:20] + "..." if len(r['nombre']) > 23 else r['nombre']
            if st.button(f"Quitar: {nombre_corto}", key=f"rm_{i}", use_container_width=True, type="secondary", on_click=quitar_resultado, args=(i,)):
                st.rerun()

        if i < len(st.session_state.resultados) - 1:
            st.markdown("---")

    # Descarga ZIP y limpiar
    st.markdown("---")
    if len(st.session_state.resultados) > 1:
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
            nombres_usados = {}
            for i, r in enumerate(st.session_state.resultados):
                texto_actual = st.session_state.get(f"txt_{i}", r['descripcion'])
                exif_zip = agregar_exif(r['imagen'], texto_actual) if guardar_exif else None
                img_bytes = imagen_a_bytes(r['imagen'], exif_zip)
                # Evitar nombres duplicados en el ZIP
                nombre = r['nombre']
                if nombre in nombres_usados:
                    nombres_usados[nombre] += 1
                    base, ext = nombre.rsplit('.', 1)
                    nombre = f"{base}_{nombres_usados[nombre]}.{ext}"
                else:
                    nombres_usados[nombre] = 0
                zf.writestr(nombre, img_bytes.getvalue())
        zip_buffer.seek(0)

        col1, col2 = st.columns([3, 1])
        with col1:
            st.download_button(
                "Descargar todo en ZIP",
                data=zip_buffer.getvalue(),
                file_name="garytext_imagenes.zip",
                mime="application/zip",
                key="dl_zip",
                use_container_width=True,
                on_click=marcar_descarga_zip
            )
        with col2:
            if st.button("Limpiar todo", use_container_width=True, type="secondary", on_click=limpiar_todo):
                st.rerun()
    else:
        if st.button("Limpiar y procesar nuevas imágenes", use_container_width=True, type="secondary", on_click=limpiar_todo):
            st.rerun()

# Footer con contadores
st.markdown(f"""
<div class="rasta-footer">
    <p style="margin-bottom: 0.3rem; font-size: 0.85rem;">
        <span aria-hidden="true">👁️</span> {contadores.get('visitas', 0):,} visitas · <span aria-hidden="true">📊</span> {contadores.get('imagenes', 0):,} imágenes analizadas
    </p>
    <p style="margin-bottom: 0.5rem;">GaryText Pro v0.1 - Por Gary Dev</p>
    <p style="font-size: 0.9rem; margin-bottom: 0.5rem;">
        Si te ha parecido útil esta aplicación, no dudes en donarme un café
    </p>
    <a href="https://ko-fi.com/garydev" target="_blank" rel="noopener noreferrer">
        <img src="https://storage.ko-fi.com/cdn/kofi2.png?v=3" alt="Donar un café en Ko-fi" style="height: 36px; border: 0;">
    </a>
</div>
""", unsafe_allow_html=True)

# Contador de visitas con JavaScript (al final para no interferir con lectores de pantalla)
components.html(f"""
<script>
(function() {{
    try {{ if (window.frameElement) {{
        window.frameElement.setAttribute('aria-hidden', 'true');
        window.frameElement.tabIndex = -1;
        window.frameElement.title = '';
    }} }} catch(e) {{}}

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
                headers: {{ "Content-Type": "application/json", "X-Master-Key": API_KEY }},
                body: JSON.stringify(datos)
            }});
        }})
        .catch(err => console.log("Error contador:", err));
    }}
}})();
</script>
""", height=0)
