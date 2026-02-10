"""Módulo de IA: configuración y generación de descripciones con Gemini"""

import logging
import re
import time
import streamlit as st
import google.generativeai as genai

log = logging.getLogger("garytext")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY", "")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)


@st.cache_resource
def obtener_modelo_gemini():
    """Cachea el modelo Gemini para reutilizarlo"""
    return genai.GenerativeModel('gemini-2.5-flash-lite')


_PREFIJOS_ES = re.compile(
    r'^(en esta imagen,?\s*|en la imagen,?\s*|la imagen muestra\s*|'
    r'se muestra\s*|se observa\s*|se puede ver\s*|es una?\s+|'
    r'esta imagen muestra\s*|vemos\s*|aquí se ve\s*|podemos ver\s*)',
    re.IGNORECASE
)
_PREFIJOS_EN = re.compile(
    r'^(in this image,?\s*|the image shows\s*|this image shows\s*|'
    r'it shows\s*|we can see\s*|there is\s*|this is a\s*|'
    r'here we see\s*|the picture shows\s*)',
    re.IGNORECASE
)


def _limpiar_descripcion(texto, idioma="es"):
    """Elimina prefijos genéricos que no aportan como alt-text"""
    patron = _PREFIJOS_ES if idioma == "es" else _PREFIJOS_EN
    limpio = patron.sub('', texto).strip()
    if limpio:
        # Asegurar que empiece con mayúscula
        limpio = limpio[0].upper() + limpio[1:]
    return limpio or texto


def describir_imagen(imagen, idioma="es", reintentos=2):
    """Genera descripción de imagen usando Gemini con reintentos automáticos"""
    if not GEMINI_API_KEY:
        return "Error: API key de Gemini no configurada"

    if imagen.mode != 'RGB':
        imagen = imagen.convert('RGB')

    model = obtener_modelo_gemini()

    if idioma == "es":
        prompt = """Analiza esta imagen y responde en este formato exacto:

NOMBRE: [3-5 palabras descriptivas que identifiquen claramente el contenido, ejemplo: "chef preparando sushi japonés" o "niños jugando en parque"]
DESCRIPCION: [Frase descriptiva detallada de 15-25 palabras que empiece con el sujeto principal]

Reglas:
- El NOMBRE debe ser claro y entendible por sí solo
- IMPORTANTE: La DESCRIPCION debe empezar directamente con el sujeto principal de la imagen (persona, objeto, lugar)
- PROHIBIDO empezar la DESCRIPCION con: "En esta imagen", "En la imagen", "La imagen muestra", "Se muestra", "Se observa", "Se puede ver", "Es una", "Esta imagen", "Vemos"
- Ejemplo correcto: "Niño sonriente sostiene un globo rojo en un parque soleado con árboles al fondo"
- Ejemplo incorrecto: "En esta imagen se muestra un niño sonriente con un globo"
- Usa español estándar neutro, evita regionalismos (ejemplo: usa "sandalias" en vez de "chanclas" o "chalas")
- Responde solo en español"""
    else:
        prompt = """Analyze this image and respond in this exact format:

NAME: [3-5 descriptive words that clearly identify the content, example: "chef preparing japanese sushi" or "children playing in park"]
DESCRIPTION: [Detailed descriptive sentence of 15-25 words starting with the main subject]

Rules:
- The NAME must be clear and understandable on its own
- IMPORTANT: The DESCRIPTION must start directly with the main subject of the image (person, object, place)
- FORBIDDEN to start the DESCRIPTION with: "In this image", "The image shows", "This image", "It shows", "We can see", "There is", "This is a"
- Correct example: "Smiling child holds a red balloon in a sunny park with trees in the background"
- Incorrect example: "In this image we can see a smiling child with a balloon"
- Respond only in English"""

    for intento in range(reintentos):
        try:
            log.info(f"Enviando request a Gemini (intento {intento + 1}/{reintentos})")
            inicio = time.time()
            response = model.generate_content([prompt, imagen])
            duracion = time.time() - inicio
            texto = response.text.strip()
            log.info(f"Respuesta recibida en {duracion:.1f}s ({len(texto)} chars)")

            # Parsear respuesta para extraer nombre y descripción
            nombre = ""
            descripcion = texto

            for linea in texto.split('\n'):
                linea = linea.strip()
                if linea.upper().startswith('NOMBRE:') or linea.upper().startswith('NAME:'):
                    nombre = linea.split(':', 1)[1].strip()
                elif linea.upper().startswith('DESCRIPCION:') or linea.upper().startswith('DESCRIPTION:'):
                    descripcion = linea.split(':', 1)[1].strip()

            # Limpiar prefijos no deseados de la descripción
            descripcion = _limpiar_descripcion(descripcion, idioma)

            # Si no se pudo parsear, usar el texto completo
            if not nombre:
                nombre = descripcion[:50] if descripcion else texto[:50]

            log.info(f"Imagen procesada OK: '{nombre}'")
            return {"nombre": nombre, "descripcion": descripcion}
        except Exception as e:
            log.warning(f"Error en intento {intento + 1}/{reintentos}: {str(e)}")
            if "429" in str(e) and intento < reintentos - 1:
                log.info("Esperando 4s antes de reintentar...")
                time.sleep(4)
                continue
            log.error(f"Error definitivo: {str(e)}")
            return {"nombre": "error", "descripcion": f"Error al procesar: {str(e)}"}

    return {"nombre": "error", "descripcion": "Error: No se pudo procesar después de varios intentos"}
