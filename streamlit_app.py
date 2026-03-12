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

# Inyecciones de accesibilidad y SEO en el documento padre (WCAG 3.1.1 / Lighthouse)
# — Este iframe se ejecuta en el mismo origen que la app Streamlit,
#   por lo que window.parent.document es accesible.
# — MutationObserver garantiza que actuamos DESPUÉS de que Streamlit renderice el DOM.
components.html("""
<script>
(function() {
    var d;
    try { d = window.parent.document; } catch(e) { return; }

    // Ocultar este iframe del árbol de accesibilidad
    try {
        if (window.frameElement) {
            window.frameElement.setAttribute('aria-hidden', 'true');
            window.frameElement.tabIndex = -1;
            window.frameElement.title = '';
            window.frameElement.style.cssText =
                'position:absolute;width:0;height:0;overflow:hidden;opacity:0;pointer-events:none;border:0';
        }
    } catch(e) {}

    // ① lang="es" — se puede hacer de inmediato
    try { d.documentElement.setAttribute('lang', 'es'); } catch(e) {}

    // ② Meta description en <head> — Lighthouse solo busca en document.head
    try {
        if (!d.head.querySelector('meta[name="description"]')) {
            var m = d.createElement('meta');
            m.setAttribute('name', 'description');
            m.setAttribute('content', 'Generador de Alt Text gratuito con IA. Mejora la accesibilidad de tus imágenes en segundos con GaryText Pro.');
            d.head.appendChild(m);
        }
    } catch(e) {}

    // ③ Aplica role="main", aria-labels en formularios y width/height en imágenes
    function applyAll() {
        try {
            // Limpiar clase de animación (se reactiva solo si hay procesamiento activo)
            d.body.classList.remove('rasta-processing');

            // role="main" en el contenedor principal de Streamlit
            var stMain = d.querySelector('[data-testid="stMain"]');
            if (stMain && !stMain.getAttribute('role')) {
                stMain.setAttribute('role', 'main');
                stMain.setAttribute('aria-label', 'Contenido principal');
            }

            // aria-label en inputs de archivo (Streamlit no genera <label for="">)
            d.querySelectorAll('input[type="file"]').forEach(function(inp) {
                if (!inp.getAttribute('aria-label') && !inp.getAttribute('aria-labelledby')) {
                    var container = inp.closest('[data-testid="stFileUploader"]');
                    var lbl = container && container.querySelector('label');
                    inp.setAttribute('aria-label', lbl ? lbl.textContent.trim() : 'Examinar archivos. Formatos: JPG, PNG, WEBP');
                }
            });

            // for/id en text areas (Streamlit no siempre genera la asociación)
            d.querySelectorAll('[data-testid="stTextArea"]').forEach(function(el) {
                var label = el.querySelector('label');
                var ta = el.querySelector('textarea');
                if (label && ta && !label.getAttribute('for')) {
                    if (!ta.id) ta.id = 'ta-' + Math.random().toString(36).slice(2, 9);
                    label.setAttribute('for', ta.id);
                }
            });

            // width/height explícitos en imágenes de st.image (evita CLS)
            d.querySelectorAll('[data-testid="stImage"] img').forEach(function(img) {
                if (img.naturalWidth && !img.hasAttribute('width')) {
                    img.setAttribute('width', img.naturalWidth);
                    img.setAttribute('height', img.naturalHeight);
                }
            });

            // Ocultar label del uploader de lectores de pantalla (la info está en "Formatos:" arriba)
            d.querySelectorAll('[data-testid="stFileUploader"] label').forEach(function(lbl) {
                lbl.setAttribute('aria-hidden', 'true');
            });

            // Botón: solo para lectores de pantalla → "Examinar archivos"
            d.querySelectorAll('[data-testid="stFileUploader"] section button').forEach(function(btn) {
                btn.setAttribute('aria-label', 'Examinar archivos');
            });

            // Ocultar contenido visual drag-and-drop con inert (más fiable en Chrome que aria-hidden)
            // inert elimina el elemento del árbol de accesibilidad sin afectar a sus hermanos
            d.querySelectorAll('[data-testid="stFileUploader"] section').forEach(function(sec) {
                Array.from(sec.children).forEach(function(child) {
                    var tag = child.tagName.toLowerCase();
                    if (tag !== 'button' && tag !== 'input') {
                        child.setAttribute('inert', '');
                        child.setAttribute('aria-hidden', 'true'); // fallback navegadores antiguos
                    }
                });
            });

        } catch(e) {}
    }

    // Ejecutar ahora y luego mantener observer para reruns de Streamlit
    applyAll();
    var debounce;
    try {
        new MutationObserver(function() {
            clearTimeout(debounce);
            debounce = setTimeout(applyAll, 250);
        }).observe(d.body, { childList: true, subtree: true });
    } catch(e) {}
})();
</script>
""", height=0)

# Estado inicial
_DEFAULTS = {
    'resultados': [],
    'archivos_previos': set(),
    'uploader_key': 0,
    'mensaje_alerta': "",
    'mostrar_visual': False,
    'error_procesamiento': False,
    'procesando_indice': -1,
    'foco_resultados': False,
    'foco_subir': False,
    'categoria_elegida': "General",
    'categoria_cambio': False,
    'idioma_elegido': "Español",
    'idioma_cambio': False,
}
for _k, _v in _DEFAULTS.items():
    if _k not in st.session_state:
        st.session_state[_k] = _v

# Funciones de callback
def marcar_descarga(nombre_archivo="todas las imágenes en archivo ZIP"):
    st.session_state.mensaje_alerta = f"Descarga completada: {nombre_archivo}"
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


# SELECTOR DE IDIOMA
OPCIONES_IDIOMA = ["Español", "English", "Português"]
IDIOMA_CODIGO = {"Español": "es", "English": "en", "Português": "pt"}
guardar_exif = True  # siempre activo

def _seleccionar_idioma(idioma):
    st.session_state.idioma_elegido = idioma
    st.session_state.idioma_cambio = True

idioma_actual = st.session_state.idioma_elegido
with st.expander(f"Idioma: {idioma_actual}"):
    for idioma_nombre in OPCIONES_IDIOMA:
        es_seleccionado = idioma_nombre == idioma_actual
        st.button(
            f"✓ {idioma_nombre}" if es_seleccionado else idioma_nombre,
            on_click=_seleccionar_idioma,
            args=(idioma_nombre,),
            use_container_width=True,
            key=f"btn_idioma_{idioma_nombre.lower()}",
            type="primary" if es_seleccionado else "secondary"
        )
idioma_codigo = IDIOMA_CODIGO[idioma_actual]

if st.session_state.idioma_cambio:
    st.session_state.idioma_cambio = False
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
            var expanders = doc.querySelectorAll('[data-testid="stExpander"]');
            for (var i = 0; i < expanders.length; i++) {{
                var summary = expanders[i].querySelector('summary');
                if (summary && summary.textContent.indexOf('Idioma:') !== -1) {{
                    var details = expanders[i].querySelector('details');
                    if (details) details.removeAttribute('open');
                    setTimeout(function() {{ summary.focus(); }}, 100);
                    break;
                }}
            }}
        }}, 300);
    }})();
    </script>
    """, height=0)

# CATEGORÍA DE ANÁLISIS
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
    label_visibility="visible"
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
    # Activar animación rasta vía clase CSS (la clase se limpia en applyAll al terminar)
    components.html(f"""
    <script>
    // {time.time()}
    (function() {{
        try {{ if (window.frameElement) {{
            window.frameElement.setAttribute('aria-hidden', 'true');
            window.frameElement.tabIndex = -1;
            window.frameElement.style.display = 'none';
        }} }} catch(e) {{}}
        try {{ window.parent.document.body.classList.add('rasta-processing'); }} catch(e) {{}}
    }})();
    </script>
    """, height=0)

    idx = st.session_state.procesando_indice
    total = len(archivos)

    if idx < total and not st.session_state.error_procesamiento:
        # Barra de progreso visual + anuncio para lectores de pantalla
        st.progress(idx / total, text=f"Procesando imagen {idx + 1} de {total}...")
        st.markdown(f'<div role="status" aria-live="polite" class="sr-only">Procesando imagen {idx + 1} de {total}</div>', unsafe_allow_html=True)

        try:
            # Delay para rate limit (solo entre imágenes, no antes de la primera)
            if idx > 0:
                time.sleep(1)

            archivo = archivos[idx]
            imagen = Image.open(archivo)
            if imagen.mode != 'RGB':
                imagen = imagen.convert('RGB')

            resultado = describir_imagen(imagen, idioma_codigo, categoria_codigo)

            nombre_nuevo = f"{limpiar_nombre(resultado['nombre'])}.jpg"
            descripcion = resultado['descripcion']

            st.session_state.resultados.append({
                "nombre": nombre_nuevo,
                "descripcion": descripcion,
                "imagen": imagen,
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
                actualizar_contadores(imagenes=total, datos_actuales=contadores)
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
            st.image(r['imagen'], width=100)
        with col_info:
            st.markdown(f"**{r['nombre']}**")
            st.text_area(
                f"Texto alternativo imagen {i+1}",
                value=r['descripcion'],
                key=f"txt_{i}",
                height=100,
                label_visibility="visible",
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
            if st.button(f"Quitar imagen {i+1}", key=f"rm_{i}", use_container_width=True, type="secondary", on_click=quitar_resultado, args=(i,)):
                st.rerun()

        if i < len(st.session_state.resultados) - 1:
            st.markdown('<hr aria-hidden="true">', unsafe_allow_html=True)

    # Descarga ZIP y limpiar
    st.markdown('<hr aria-hidden="true">', unsafe_allow_html=True)
    if len(st.session_state.resultados) > 1:
        # Reconstruir ZIP solo si cambiaron nombres o descripciones
        zip_fingerprint = tuple(
            (r['nombre'], st.session_state.get(f"txt_{i}", r['descripcion']))
            for i, r in enumerate(st.session_state.resultados)
        )
        if st.session_state.get('_zip_fingerprint') != zip_fingerprint:
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
                nombres_usados = {}
                for i, r in enumerate(st.session_state.resultados):
                    texto_actual = st.session_state.get(f"txt_{i}", r['descripcion'])
                    exif_zip = agregar_exif(r['imagen'], texto_actual) if guardar_exif else None
                    img_bytes = imagen_a_bytes(r['imagen'], exif_zip)
                    nombre = r['nombre']
                    if nombre in nombres_usados:
                        nombres_usados[nombre] += 1
                        base, ext = nombre.rsplit('.', 1)
                        nombre = f"{base}_{nombres_usados[nombre]}.{ext}"
                    else:
                        nombres_usados[nombre] = 0
                    zf.writestr(nombre, img_bytes.getvalue())
            st.session_state['_zip_cache'] = zip_buffer.getvalue()
            st.session_state['_zip_fingerprint'] = zip_fingerprint

        col1, col2 = st.columns([3, 1])
        with col1:
            st.download_button(
                "Descargar todo en ZIP",
                data=st.session_state['_zip_cache'],
                file_name="garytext_imagenes.zip",
                mime="application/zip",
                key="dl_zip",
                use_container_width=True,
                on_click=marcar_descarga
            )
        with col2:
            if st.button("Limpiar todo", use_container_width=True, type="secondary", on_click=limpiar_todo):
                st.rerun()
    else:
        if st.button("Limpiar y procesar nuevas imágenes", use_container_width=True, type="secondary", on_click=limpiar_todo):
            st.rerun()

    # Banner consultoría
    st.markdown("""
<div class="banner-consultoria">
    <p class="titulo">¿Tu sitio web necesita una auditoría de accesibilidad?</p>
    <p>El alt text es solo el comienzo. Ofrezco auditorías WCAG 2.2, testing manual con NVDA, JAWS y VoiceOver, y revisión de código.</p>
    <a href="https://digitalaccessibility.cl" target="_blank" rel="noopener noreferrer">
        Ver servicios en digitalaccessibility.cl
        <span class="sr-only"> (se abre en nueva pestaña)</span>
    </a>
</div>
""", unsafe_allow_html=True)

st.divider()

# Footer con contadores
st.markdown(f"""
<div class="rasta-footer">
    <p class="footer-stats">
        <span aria-hidden="true">👁️</span> {contadores.get('visitas', 0):,} visitas · <span aria-hidden="true">📊</span> {contadores.get('imagenes', 0):,} imágenes analizadas
    </p>
    <p class="footer-credits" role="text">© 2026
        <a href="https://digitalaccessibility.cl" target="_blank" rel="noopener noreferrer">GaryDev
            <span class="sr-only"> (se abre en nueva pestaña)</span>
        </a> · Todos los derechos reservados.
    </p>
    <p class="footer-donate">Si te ha parecido útil esta aplicación, no dudes en donarme un café</p>
    <a href="https://ko-fi.com/garydev" target="_blank" rel="noopener noreferrer">
        <img src="https://storage.ko-fi.com/cdn/kofi2.png?v=3" alt="Donar un café en Ko-fi" width="143" height="36" loading="eager" style="border:0;">
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
