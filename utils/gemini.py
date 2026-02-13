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


PROMPTS_CATEGORIAS = {
    "general": {
        "es": """Analiza esta imagen y responde en este formato exacto:

NOMBRE: [3-5 palabras descriptivas que identifiquen claramente el contenido, ejemplo: "chef preparando sushi japonés" o "niños jugando en parque"]
DESCRIPCION: [Frase descriptiva detallada de 15-25 palabras que empiece con el sujeto principal]

Reglas:
- El NOMBRE debe ser claro y entendible por sí solo
- IMPORTANTE: La DESCRIPCION debe empezar directamente con el sujeto principal de la imagen (persona, objeto, lugar)
- PROHIBIDO empezar la DESCRIPCION con: "En esta imagen", "En la imagen", "La imagen muestra", "Se muestra", "Se observa", "Se puede ver", "Es una", "Esta imagen", "Vemos"
- Ejemplo correcto: "Niño sonriente sostiene un globo rojo en un parque soleado con árboles al fondo"
- Ejemplo incorrecto: "En esta imagen se muestra un niño sonriente con un globo"
- Usa español estándar neutro, evita regionalismos (ejemplo: usa "sandalias" en vez de "chanclas" o "chalas")
- Responde solo en español""",
        "en": """Analyze this image and respond in this exact format:

NAME: [3-5 descriptive words that clearly identify the content, example: "chef preparing japanese sushi" or "children playing in park"]
DESCRIPTION: [Detailed descriptive sentence of 15-25 words starting with the main subject]

Rules:
- The NAME must be clear and understandable on its own
- IMPORTANT: The DESCRIPTION must start directly with the main subject of the image (person, object, place)
- FORBIDDEN to start the DESCRIPTION with: "In this image", "The image shows", "This image", "It shows", "We can see", "There is", "This is a"
- Correct example: "Smiling child holds a red balloon in a sunny park with trees in the background"
- Incorrect example: "In this image we can see a smiling child with a balloon"
- Respond only in English"""
    },
    "personas": {
        "es": """Analiza a la persona o personas en esta imagen y responde en este formato exacto:

NOMBRE: [3-5 palabras identificando a la persona, ejemplo: "mujer joven cabello castaño" o "hombre mayor barba gris"]
DESCRIPCION: [Descripción detallada de 20-40 palabras que incluya: género (hombre/mujer), edad aproximada, contextura corporal (delgado, robusto, gordo, atlético), color de piel, color y tipo de cabello (liso, rizado, corto, largo), y rasgos faciales destacados]

Reglas:
- IMPORTANTE: La DESCRIPCION debe empezar directamente con "Hombre" o "Mujer" seguido de la edad aproximada
- Sé objetivo y respetuoso al describir características físicas
- Si hay varias personas, describe la más prominente
- Usa español estándar neutro
- PROHIBIDO empezar con: "En esta imagen", "Se muestra", "Se observa", "Se puede ver"
- Responde solo en español""",
        "en": """Analyze the person or people in this image and respond in this exact format:

NAME: [3-5 words identifying the person, example: "young woman brown hair" or "older man gray beard"]
DESCRIPTION: [Detailed description of 20-40 words including: gender (man/woman), approximate age, body build (slim, robust, heavy, athletic), skin color, hair color and type (straight, curly, short, long), and notable facial features]

Rules:
- IMPORTANT: The DESCRIPTION must start directly with "Man" or "Woman" followed by approximate age
- Be objective and respectful when describing physical characteristics
- If there are multiple people, describe the most prominent one
- FORBIDDEN to start with: "In this image", "The image shows", "We can see", "There is"
- Respond only in English"""
    },
    "vestuario": {
        "es": """Analiza la vestimenta y accesorios en esta imagen y responde en este formato exacto:

NOMBRE: [3-5 palabras describiendo el atuendo principal, ejemplo: "vestido rojo elegante fiesta" o "traje formal azul marino"]
DESCRIPCION: [Descripción detallada de 20-40 palabras que incluya: tipo de prenda (pantalón, polera, vestido, falda, chaqueta, zapatillas, zapatos, etc.), color de cada prenda, textura o material visible (algodón, cuero, mezclilla, seda), estilo general (casual, formal, deportivo), marca si es identificable, y complementos/accesorios (bolso, reloj, gafas, sombrero, joyas)]

Reglas:
- IMPORTANTE: La DESCRIPCION debe empezar directamente con la prenda principal
- Describe de arriba a abajo: cabeza, torso, piernas, calzado
- Menciona colores específicos (no solo "claro" u "oscuro")
- Usa español estándar neutro (polera, zapatillas, pantalón)
- PROHIBIDO empezar con: "En esta imagen", "Se muestra", "Se observa", "Se puede ver"
- Responde solo en español""",
        "en": """Analyze the clothing and accessories in this image and respond in this exact format:

NAME: [3-5 words describing the main outfit, example: "elegant red party dress" or "formal navy blue suit"]
DESCRIPTION: [Detailed description of 20-40 words including: garment type (pants, shirt, dress, skirt, jacket, sneakers, shoes, etc.), color of each item, visible texture or material (cotton, leather, denim, silk), overall style (casual, formal, sporty), brand if identifiable, and accessories (bag, watch, glasses, hat, jewelry)]

Rules:
- IMPORTANT: The DESCRIPTION must start directly with the main garment
- Describe top to bottom: head, torso, legs, footwear
- Mention specific colors (not just "light" or "dark")
- FORBIDDEN to start with: "In this image", "The image shows", "We can see", "There is"
- Respond only in English"""
    },
    "paisajes": {
        "es": """Analiza el paisaje en esta imagen y responde en este formato exacto:

NOMBRE: [3-5 palabras describiendo el paisaje, ejemplo: "lago montañas atardecer otoño" o "playa tropical arena blanca"]
DESCRIPCION: [Descripción detallada de 20-40 palabras que incluya: elementos naturales presentes (árboles, ríos, lagos, montañas, caminos, flores, rocas), construcciones si las hay (casas, puentes, cercas), colores predominantes, clima aparente (soleado, nublado, lluvioso, nevado), momento del día, y ambiente/sensación que transmite (tranquilo, acogedor, frío, caluroso, misterioso, vibrante)]

Reglas:
- IMPORTANTE: La DESCRIPCION debe empezar directamente con el elemento más destacado del paisaje
- Incluye la paleta de colores dominante
- Menciona el clima y la sensación/ambiente que transmite
- Usa español estándar neutro
- PROHIBIDO empezar con: "En esta imagen", "Se muestra", "Se observa", "Se puede ver"
- Responde solo en español""",
        "en": """Analyze the landscape in this image and respond in this exact format:

NAME: [3-5 words describing the landscape, example: "mountain lake autumn sunset" or "tropical beach white sand"]
DESCRIPTION: [Detailed description of 20-40 words including: natural elements present (trees, rivers, lakes, mountains, paths, flowers, rocks), constructions if any (houses, bridges, fences), predominant colors, apparent weather (sunny, cloudy, rainy, snowy), time of day, and mood/atmosphere (peaceful, cozy, cold, warm, mysterious, vibrant)]

Rules:
- IMPORTANT: The DESCRIPTION must start directly with the most prominent landscape element
- Include the dominant color palette
- Mention the weather and the feeling/atmosphere it conveys
- FORBIDDEN to start with: "In this image", "The image shows", "We can see", "There is"
- Respond only in English"""
    }
}


def describir_imagen(imagen, idioma="es", categoria="general", reintentos=2):
    """Genera descripción de imagen usando Gemini con reintentos automáticos"""
    if not GEMINI_API_KEY:
        return "Error: API key de Gemini no configurada"

    if imagen.mode != 'RGB':
        imagen = imagen.convert('RGB')

    model = obtener_modelo_gemini()

    prompt = PROMPTS_CATEGORIAS.get(categoria, PROMPTS_CATEGORIAS["general"])[idioma]

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
