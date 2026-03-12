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
    return genai.GenerativeModel('gemini-2.5-flash')


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
_PREFIJOS_PT = re.compile(
    r'^(nesta imagem,?\s*|a imagem mostra\s*|esta imagem mostra\s*|'
    r'podemos ver\s*|há um\s*|há uma\s*|aqui vemos\s*|'
    r'mostra\s*|vemos\s*|trata-se de\s*)',
    re.IGNORECASE
)


def _limpiar_descripcion(texto, idioma="es"):
    """Elimina prefijos genéricos que no aportan como alt-text"""
    if idioma == "en":
        patron = _PREFIJOS_EN
    elif idioma == "pt":
        patron = _PREFIJOS_PT
    else:
        patron = _PREFIJOS_ES
    limpio = patron.sub('', texto).strip()
    if limpio:
        limpio = limpio[0].upper() + limpio[1:]
    return limpio or texto


PROMPTS_CATEGORIAS = {
    "general": {
        "es": """Eres un experto en accesibilidad web especializado en redacción de texto alternativo (alt text) según las pautas WCAG 2.2. Tu tarea es generar descripciones precisas, concisas y útiles para personas con discapacidad visual que usan lectores de pantalla.

Analiza esta imagen y responde ÚNICAMENTE en este formato exacto (sin texto adicional):

NOMBRE: [3-5 palabras clave que identifiquen el contenido principal, ejemplo: "chef preparando sushi japonés" o "niños jugando en parque"]
DESCRIPCION: [Alt text profesional de 15-30 palabras: describe el sujeto principal, su acción o estado, y el contexto relevante. Sé específico con colores, formas y detalles que aporten valor.]

Criterios de calidad para la DESCRIPCION:
- Empieza directamente con el sujeto principal (persona, objeto, lugar, concepto)
- Incluye la acción o estado si es relevante (corriendo, sonriendo, iluminado por el sol)
- Menciona el contexto o fondo si aporta significado
- Usa adjetivos precisos (no "grande" sino "de tamaño considerable"; no "bonito" sino el atributo concreto)
- Si la imagen contiene texto legible, inclúyelo entre comillas
- Si la imagen es ambigua o de baja calidad, describe lo que se puede distinguir con certeza
- PROHIBIDO empezar con: "En esta imagen", "En la imagen", "La imagen muestra", "Se muestra", "Se observa", "Se puede ver", "Es una", "Esta imagen", "Vemos", "Aquí"
- Usa español estándar neutro (evita regionalismos)
- Responde solo en español""",

        "en": """You are a web accessibility expert specialized in writing alternative text (alt text) according to WCAG 2.2 guidelines. Your task is to generate precise, concise and useful descriptions for people with visual disabilities who use screen readers.

Analyze this image and respond ONLY in this exact format (no additional text):

NAME: [3-5 keywords that clearly identify the main content, example: "chef preparing japanese sushi" or "children playing in park"]
DESCRIPTION: [Professional alt text of 15-30 words: describe the main subject, its action or state, and relevant context. Be specific about colors, shapes and details that add value.]

Quality criteria for the DESCRIPTION:
- Start directly with the main subject (person, object, place, concept)
- Include the action or state if relevant (running, smiling, sunlit)
- Mention context or background if it adds meaning
- Use precise adjectives (not "big" but the specific measurement; not "pretty" but the concrete attribute)
- If the image contains readable text, include it in quotes
- If the image is ambiguous or low quality, describe only what can be distinguished with certainty
- FORBIDDEN to start with: "In this image", "The image shows", "This image", "It shows", "We can see", "There is", "This is a", "Here we see"
- Respond only in English""",

        "pt": """Você é um especialista em acessibilidade web especializado em redação de texto alternativo (alt text) de acordo com as diretrizes WCAG 2.2. Sua tarefa é gerar descrições precisas, concisas e úteis para pessoas com deficiência visual que usam leitores de tela.

Analise esta imagem e responda APENAS neste formato exato (sem texto adicional):

NOME: [3-5 palavras-chave que identifiquem claramente o conteúdo principal, exemplo: "chef preparando sushi japonês" ou "crianças brincando no parque"]
DESCRICAO: [Alt text profissional de 15-30 palavras: descreva o sujeito principal, sua ação ou estado, e o contexto relevante. Seja específico com cores, formas e detalhes que agregam valor.]

Critérios de qualidade para a DESCRICAO:
- Comece diretamente com o sujeito principal (pessoa, objeto, lugar, conceito)
- Inclua a ação ou estado se relevante (correndo, sorrindo, iluminado pelo sol)
- Mencione o contexto ou fundo se agregar significado
- Use adjetivos precisos (não "grande" mas o atributo concreto; não "bonito" mas a característica específica)
- Se a imagem contiver texto legível, inclua-o entre aspas
- Se a imagem for ambígua ou de baixa qualidade, descreva apenas o que pode ser distinguido com certeza
- PROIBIDO começar com: "Nesta imagem", "A imagem mostra", "Esta imagem", "Mostra", "Podemos ver", "Há um", "Aqui vemos"
- Use português brasileiro padrão
- Responda apenas em português"""
    },

    "personas": {
        "es": """Eres un experto en accesibilidad web especializado en redacción de texto alternativo (alt text) según WCAG 2.2. Tu tarea es describir personas de forma objetiva, respetuosa y útil para usuarios de lectores de pantalla.

Analiza a la persona o personas principales en esta imagen y responde ÚNICAMENTE en este formato exacto:

NOMBRE: [3-5 palabras que identifiquen a la persona, ejemplo: "mujer joven cabello castaño ondulado" o "hombre adulto mayor barba canosa"]
DESCRIPCION: [Descripción objetiva y detallada de 25-45 palabras que incluya los rasgos visibles más relevantes]

Guía para construir la DESCRIPCION (incluye los elementos que sean visibles y relevantes):
1. Género aparente y rango de edad (niño/adolescente/adulto joven/adulto/adulto mayor)
2. Contextura física (delgada, atlética, robusta, corpulenta)
3. Tono de piel (claro, moreno claro, moreno, oscuro, negro)
4. Cabello: color (negro, castaño, rubio, pelirrojo, gris, blanco), largo (corto, medio, largo) y tipo (liso, ondulado, rizado, afro)
5. Rasgos faciales destacados si son visibles (barba, bigote, lentes, pecas)
6. Expresión facial (sonriente, seria, pensativa, sorprendida)
7. Postura o gesto principal (de pie, sentada, con los brazos cruzados, señalando)
8. Contexto o actividad si aporta significado (en una oficina, al aire libre, durante una reunión)

Reglas:
- Si hay varias personas, describe la más prominente o la que ocupa más espacio en la imagen
- Si el género no es claro, describe "Persona" sin asumir género
- Sé objetivo: describe características físicas sin juicios de valor ni estereotipos
- PROHIBIDO empezar con: "En esta imagen", "Se muestra", "Se observa", "Se puede ver", "Vemos"
- Usa español estándar neutro
- Responde solo en español""",

        "en": """You are a web accessibility expert specialized in writing alternative text (alt text) according to WCAG 2.2. Your task is to describe people objectively, respectfully and usefully for screen reader users.

Analyze the main person or people in this image and respond ONLY in this exact format:

NAME: [3-5 words identifying the person, example: "young woman wavy brown hair" or "elderly man gray beard glasses"]
DESCRIPTION: [Objective and detailed description of 25-45 words including the most relevant visible features]

Guide for building the DESCRIPTION (include elements that are visible and relevant):
1. Apparent gender and age range (child/teen/young adult/adult/senior)
2. Body build (slim, athletic, robust, heavyset)
3. Skin tone (light, medium-light, medium, medium-dark, dark)
4. Hair: color (black, brown, blonde, red, gray, white), length (short, medium, long) and type (straight, wavy, curly, coily)
5. Notable facial features if visible (beard, mustache, glasses, freckles)
6. Facial expression (smiling, serious, thoughtful, surprised)
7. Main posture or gesture (standing, seated, arms crossed, pointing)
8. Context or activity if meaningful (in an office, outdoors, during a meeting)

Rules:
- If there are multiple people, describe the most prominent or largest in frame
- If gender is unclear, describe "Person" without assuming gender
- Be objective: describe physical characteristics without value judgments or stereotypes
- FORBIDDEN to start with: "In this image", "The image shows", "We can see", "There is", "Here we see"
- Respond only in English""",

        "pt": """Você é um especialista em acessibilidade web especializado em redação de texto alternativo (alt text) de acordo com as diretrizes WCAG 2.2. Sua tarefa é descrever pessoas de forma objetiva, respeitosa e útil para usuários de leitores de tela.

Analise a pessoa ou pessoas principais nesta imagem e responda APENAS neste formato exato:

NOME: [3-5 palavras que identifiquem a pessoa, exemplo: "mulher jovem cabelo castanho ondulado" ou "homem idoso barba grisalha óculos"]
DESCRICAO: [Descrição objetiva e detalhada de 25-45 palavras incluindo os traços visíveis mais relevantes]

Guia para construir a DESCRICAO (inclua os elementos visíveis e relevantes):
1. Gênero aparente e faixa etária (criança/adolescente/adulto jovem/adulto/idoso)
2. Biotipo (magro, atlético, robusto, corpulento)
3. Tom de pele (claro, médio claro, médio, médio escuro, escuro)
4. Cabelo: cor (preto, castanho, loiro, ruivo, grisalho, branco), comprimento (curto, médio, longo) e tipo (liso, ondulado, cacheado, crespo)
5. Traços faciais notáveis se visíveis (barba, bigode, óculos, sardas)
6. Expressão facial (sorridente, séria, pensativa, surpresa)
7. Postura ou gesto principal (em pé, sentado, braços cruzados, apontando)
8. Contexto ou atividade se significativo (em escritório, ao ar livre, em reunião)

Regras:
- Se houver várias pessoas, descreva a mais proeminente ou maior em cena
- Se o gênero não for claro, descreva "Pessoa" sem assumir gênero
- Seja objetivo: descreva características físicas sem julgamentos de valor ou estereótipos
- PROIBIDO começar com: "Nesta imagem", "A imagem mostra", "Podemos ver", "Há um", "Aqui vemos"
- Responda apenas em português"""
    },

    "vestuario": {
        "es": """Eres un experto en accesibilidad web y moda especializado en redacción de texto alternativo (alt text) según WCAG 2.2. Tu tarea es describir ropa y accesorios de forma detallada y útil para usuarios de lectores de pantalla, especialmente en contextos de e-commerce o moda.

Analiza la vestimenta y accesorios visibles en esta imagen y responde ÚNICAMENTE en este formato exacto:

NOMBRE: [3-5 palabras describiendo el atuendo o prenda principal, ejemplo: "vestido midi rojo floral verano" o "traje formal gris antracita hombre"]
DESCRIPCION: [Descripción detallada de 25-45 palabras del atuendo completo, de arriba hacia abajo]

Guía para construir la DESCRIPCION (describe en este orden lo que sea visible):
1. Parte superior: tipo de prenda (camiseta, blusa, camisa, suéter, chaqueta, abrigo), color exacto, patrón o estampado (liso, rayas, cuadros, flores, geométrico), material aparente (algodón, lana, seda, cuero, mezclilla, poliéster), corte o estilo (holgado, ajustado, sin mangas, manga larga, cuello redondo, escote en V)
2. Parte inferior: tipo de prenda (pantalón, falda, shorts, vestido), color, largo (mini, midi, maxi, hasta la rodilla), estilo
3. Calzado: tipo (zapatillas, zapatos, botas, sandalias, tacones), color, material si es visible
4. Accesorios: bolso/cartera (tipo, color), reloj, joyería (collares, aretes, pulseras), cinturón, sombrero, gafas, pañuelo, mochila
5. Marca si es identificable por logo o etiqueta visible
6. Estilo general del conjunto: casual, formal, deportivo, elegante, bohemio, streetwear, etc.

Reglas:
- Menciona colores específicos (no "claro" u "oscuro" sino el nombre del color: beige, burdeos, mostaza, verde oliva)
- Si la imagen muestra solo una prenda (e-commerce), descríbela en detalle
- PROHIBIDO empezar con: "En esta imagen", "Se muestra", "Se observa", "Se puede ver"
- Usa español estándar neutro (polera, zapatillas, pantalón, falda)
- Responde solo en español""",

        "en": """You are a web accessibility and fashion expert specialized in writing alternative text (alt text) according to WCAG 2.2. Your task is to describe clothing and accessories in detail for screen reader users, especially in e-commerce or fashion contexts.

Analyze the visible clothing and accessories in this image and respond ONLY in this exact format:

NAME: [3-5 words describing the main outfit or garment, example: "red floral midi dress summer" or "formal charcoal gray men suit"]
DESCRIPTION: [Detailed description of 25-45 words of the complete outfit, from top to bottom]

Guide for building the DESCRIPTION (describe in this order what is visible):
1. Top: garment type (t-shirt, blouse, shirt, sweater, jacket, coat), exact color, pattern (solid, stripes, plaid, floral, geometric), apparent material (cotton, wool, silk, leather, denim, polyester), cut or style (oversized, fitted, sleeveless, long sleeve, crew neck, V-neck)
2. Bottom: garment type (pants, skirt, shorts, dress), color, length (mini, midi, maxi, knee-length), style
3. Footwear: type (sneakers, shoes, boots, sandals, heels), color, material if visible
4. Accessories: bag/purse (type, color), watch, jewelry (necklaces, earrings, bracelets), belt, hat, glasses, scarf, backpack
5. Brand if identifiable by visible logo or label
6. Overall outfit style: casual, formal, sporty, elegant, bohemian, streetwear, etc.

Rules:
- Mention specific colors (not "light" or "dark" but the color name: beige, burgundy, mustard, olive green)
- If the image shows only one garment (e-commerce), describe it in detail
- FORBIDDEN to start with: "In this image", "The image shows", "We can see", "There is"
- Respond only in English""",

        "pt": """Você é um especialista em acessibilidade web e moda especializado em redação de texto alternativo (alt text) de acordo com as diretrizes WCAG 2.2. Sua tarefa é descrever roupas e acessórios de forma detalhada e útil para usuários de leitores de tela, especialmente em contextos de e-commerce ou moda.

Analise as roupas e acessórios visíveis nesta imagem e responda APENAS neste formato exato:

NOME: [3-5 palavras descrevendo o look ou peça principal, exemplo: "vestido midi vermelho floral verão" ou "terno formal cinza carvão masculino"]
DESCRICAO: [Descrição detalhada de 25-45 palavras do look completo, de cima para baixo]

Guia para construir a DESCRICAO (descreva nesta ordem o que for visível):
1. Parte superior: tipo de peça (camiseta, blusa, camisa, suéter, jaqueta, casaco), cor exata, padrão ou estampa (liso, listras, xadrez, flores, geométrico), material aparente (algodão, lã, seda, couro, jeans, poliéster), corte ou estilo (oversized, ajustado, sem mangas, manga longa, decote redondo, decote em V)
2. Parte inferior: tipo de peça (calça, saia, shorts, vestido), cor, comprimento (mini, midi, maxi, até o joelho), estilo
3. Calçado: tipo (tênis, sapatos, botas, sandálias, saltos), cor, material se visível
4. Acessórios: bolsa/carteira (tipo, cor), relógio, joias (colares, brincos, pulseiras), cinto, chapéu, óculos, lenço, mochila
5. Marca se identificável por logo ou etiqueta visível
6. Estilo geral do look: casual, formal, esportivo, elegante, boêmio, streetwear, etc.

Regras:
- Mencione cores específicas (não "claro" ou "escuro" mas o nome da cor: bege, bordô, mostarda, verde oliva)
- Se a imagem mostrar apenas uma peça (e-commerce), descreva-a em detalhes
- PROIBIDO começar com: "Nesta imagem", "A imagem mostra", "Podemos ver", "Há um"
- Responda apenas em português"""
    },

    "paisajes": {
        "es": """Eres un experto en accesibilidad web especializado en redacción de texto alternativo (alt text) según WCAG 2.2. Tu tarea es describir paisajes y entornos de forma evocadora, precisa y útil para personas con discapacidad visual que usan lectores de pantalla.

Analiza el paisaje o entorno en esta imagen y responde ÚNICAMENTE en este formato exacto:

NOMBRE: [3-5 palabras que capturen la esencia del paisaje, ejemplo: "lago alpino reflejos montañas otoño" o "callejón urbano nocturno lluvia neón"]
DESCRIPCION: [Descripción detallada y evocadora de 25-45 palabras que transmita tanto los elementos visuales como la atmósfera del lugar]

Guía para construir la DESCRIPCION (incluye los elementos visibles y relevantes):
1. Elemento protagonista: el elemento dominante que define la escena (cordillera nevada, playa de arena blanca, bosque denso, ciudad al atardecer, desierto rojo)
2. Elementos secundarios: lo que acompaña al protagonista (árboles, ríos, caminos, edificios, flores, rocas, nubes, personas en la distancia)
3. Paleta de colores dominante: los 2-3 colores que más caracterizan la imagen (cielo azul intenso, vegetación verde esmeralda, tierra ocre)
4. Condición climática y luz: soleado con sombras largas, nublado y difuso, lluvia intensa, niebla matinal, luz dorada del atardecer, noche estrellada
5. Momento del día: amanecer, mañana, mediodía, tarde, atardecer, noche
6. Atmósfera y sensación: la emoción o sensación que evoca (tranquilidad serena, energía vibrante, soledad melancólica, frescura revitalizante, misterio envolvente, calidez acogedora)
7. Si hay estructuras humanas: tipo (puente de piedra, faro blanco, pueblo medieval, rascacielos de cristal) y cómo se integran al paisaje

Reglas:
- Prioriza lo que hace único a este paisaje frente a otros similares
- Combina descripción objetiva con la atmósfera que transmite
- PROHIBIDO empezar con: "En esta imagen", "Se muestra", "Se observa", "Se puede ver", "Vemos"
- Usa español estándar neutro
- Responde solo en español""",

        "en": """You are a web accessibility expert specialized in writing alternative text (alt text) according to WCAG 2.2. Your task is to describe landscapes and environments in an evocative, precise and useful way for people with visual disabilities who use screen readers.

Analyze the landscape or environment in this image and respond ONLY in this exact format:

NAME: [3-5 words that capture the essence of the landscape, example: "alpine lake mountain reflections autumn" or "rainy urban alley neon night"]
DESCRIPTION: [Detailed and evocative description of 25-45 words that conveys both the visual elements and the atmosphere of the place]

Guide for building the DESCRIPTION (include visible and relevant elements):
1. Main element: the dominant element that defines the scene (snow-capped mountain range, white sand beach, dense forest, city at sunset, red desert)
2. Secondary elements: what accompanies the main subject (trees, rivers, paths, buildings, flowers, rocks, clouds, distant people)
3. Dominant color palette: the 2-3 colors that most characterize the image (deep blue sky, emerald green vegetation, ochre earth)
4. Weather and light condition: sunny with long shadows, overcast and diffuse, heavy rain, morning fog, golden sunset light, starry night
5. Time of day: dawn, morning, midday, afternoon, sunset, night
6. Atmosphere and feeling: the emotion or sensation it evokes (serene tranquility, vibrant energy, melancholic solitude, revitalizing freshness, enveloping mystery, cozy warmth)
7. If human structures are present: type (stone bridge, white lighthouse, medieval village, glass skyscraper) and how they integrate into the landscape

Rules:
- Prioritize what makes this landscape unique compared to similar ones
- Combine objective description with the atmosphere it conveys
- FORBIDDEN to start with: "In this image", "The image shows", "We can see", "There is", "Here we see"
- Respond only in English""",

        "pt": """Você é um especialista em acessibilidade web especializado em redação de texto alternativo (alt text) de acordo com as diretrizes WCAG 2.2. Sua tarefa é descrever paisagens e ambientes de forma evocativa, precisa e útil para pessoas com deficiência visual que usam leitores de tela.

Analise a paisagem ou ambiente nesta imagem e responda APENAS neste formato exato:

NOME: [3-5 palavras que capturem a essência da paisagem, exemplo: "lago alpino reflexos montanhas outono" ou "beco urbano noturno chuva néon"]
DESCRICAO: [Descrição detalhada e evocativa de 25-45 palavras que transmita tanto os elementos visuais quanto a atmosfera do lugar]

Guia para construir a DESCRICAO (inclua os elementos visíveis e relevantes):
1. Elemento protagonista: o elemento dominante que define a cena (cordilheira nevada, praia de areia branca, floresta densa, cidade ao pôr do sol, deserto vermelho)
2. Elementos secundários: o que acompanha o protagonista (árvores, rios, caminhos, edifícios, flores, rochas, nuvens, pessoas ao longe)
3. Paleta de cores dominante: as 2-3 cores que mais caracterizam a imagem (céu azul intenso, vegetação verde esmeralda, terra ocre)
4. Condição climática e luz: ensolarado com sombras longas, nublado e difuso, chuva intensa, névoa matinal, luz dourada do pôr do sol, noite estrelada
5. Momento do dia: amanhecer, manhã, meio-dia, tarde, pôr do sol, noite
6. Atmosfera e sensação: a emoção ou sensação que evoca (tranquilidade serena, energia vibrante, solidão melancólica, frescor revitalizante, mistério envolvente, aconchego acolhedor)
7. Se houver estruturas humanas: tipo (ponte de pedra, farol branco, vila medieval, arranha-céu de vidro) e como se integram à paisagem

Regras:
- Priorize o que torna esta paisagem única em relação a outras similares
- Combine descrição objetiva com a atmosfera que transmite
- PROIBIDO começar com: "Nesta imagem", "A imagem mostra", "Podemos ver", "Há um", "Aqui vemos"
- Responda apenas em português"""
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
                if linea.upper().startswith(('NOMBRE:', 'NAME:', 'NOME:')):
                    nombre = linea.split(':', 1)[1].strip()
                elif linea.upper().startswith(('DESCRIPCION:', 'DESCRIPTION:', 'DESCRICAO:')):
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
