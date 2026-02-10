"""Módulo de IA: configuración y generación de descripciones con Gemini"""

import logging
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
    return genai.GenerativeModel('gemini-2.0-flash')


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
DESCRIPCION: [Frase descriptiva detallada de 15-25 palabras]

Reglas:
- El NOMBRE debe ser claro y entendible por sí solo
- La DESCRIPCION empieza directamente con el sujeto, sin usar "Es una", "En esta imagen", "Se muestra"
- Responde solo en español"""
    else:
        prompt = """Analyze this image and respond in this exact format:

NAME: [3-5 descriptive words that clearly identify the content, example: "chef preparing japanese sushi" or "children playing in park"]
DESCRIPTION: [Detailed descriptive sentence of 15-25 words]

Rules:
- The NAME must be clear and understandable on its own
- The DESCRIPTION starts directly with the subject, without using "This is", "In this image", "It shows"
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
