# LOG DE ESTADO - GaryText Pro

**Fecha:** 6 de febrero de 2026
**Repositorio:** https://github.com/GaryMp/Generador-de-altext-para-imagenes

---

## Resumen de lo implementado

### 1. Migración a Google Gemini API
- **Antes:** Modelo BLIP local (Salesforce/blip-image-captioning-base) - lento (~10-15s/imagen)
- **Ahora:** Google Gemini 2.0 Flash API - rápido (~2-4s/imagen)
- API Key configurada en `st.secrets["GEMINI_API_KEY"]`
- Tier gratuito con facturación activa (15 RPM)

### 2. Manejo de Rate Limit
- Delay inicial de 1 segundo antes de primera imagen
- Delay de 4 segundos entre imágenes
- Sistema de reintentos automáticos (2 intentos, 4s espera)
- Modelo cacheado con `@st.cache_resource` para mejor rendimiento

### 3. Prompt Estructurado (Nombre + Descripción)
El prompt pide a Gemini dos campos separados:
```
NOMBRE: 3-5 palabras claras y significativas → nombre_archivo.jpg
DESCRIPCION: 15-25 palabras detalladas → texto alternativo
```

**Reglas del prompt:**
- Evita: "Es una", "En esta imagen", "Se muestra", "Se ve", "Hay un/una"
- Empieza directamente con el sujeto principal

### 4. Contador de Visitas Arreglado
- **Problema:** JavaScript en `st.markdown` no se ejecutaba
- **Solución:** Usar `st.components.v1.html()` que ejecuta JS en iframe
- LocalStorage para identificar visitantes únicos
- El contador se actualiza en JSONBin y se ve en próximo refresh

### 5. Estilo Visual Rasta
- Borde superior degradado (verde-amarillo-rojo) de 4px
- Título "Gary" con cada letra coloreada
- Separadores horizontales con degradado rasta
- Footer con banda de color rasta

### 6. Tema Claro Forzado
- CSS que fuerza `background-color: #ffffff` en contenedores principales
- Evita problemas con usuarios en modo oscuro

### 7. Botón de Donación Ko-fi
- URL: https://ko-fi.com/garydev
- Ubicación: Footer de la app

---

## Configuración

### JSONBin.io (Contadores)
```
BIN_ID = "6983d11b43b1c97be965ec3c"
API_KEY = "$2a$10$6j4MIEVKRPTDxuwR3GRw2unUp8KZ3TbTvl/3psM5RA7nEpMZ8ALxO"
```

### Gemini API
- Configurar en Streamlit Cloud: Settings → Secrets
```toml
GEMINI_API_KEY = "tu-api-key"
```

---

## Archivos del Proyecto
- `streamlit_app.py` - Código principal
- `requirements.txt` - Dependencias (streamlit, pillow, piexif, requests, google-generativeai)
- `.streamlit/secrets.toml.example` - Ejemplo de configuración

---

## Pendientes / Ideas Futuras
- [ ] Cuadro de preguntas adicionales por imagen analizada
- [ ] Migrar credenciales JSONBin a st.secrets
- [ ] Botones de compartir en redes sociales
- [ ] Sección de testimonios

---

## Problemas Conocidos y Soluciones

| Problema | Solución |
|----------|----------|
| JavaScript no se ejecuta en st.markdown | Usar components.html() |
| Error 429 rate limit | Delays + reintentos automáticos |
| Primera imagen falla | Delay inicial de 1s |
| Modelo lento al cargar | Cache con @st.cache_resource |

---

## Comandos Útiles
```bash
# Ver cambios locales
git status

# Subir cambios
git add .
git commit -m "Descripción del cambio"
git push

# Resetear contadores a 0
curl -X PUT "https://api.jsonbin.io/v3/b/6983d11b43b1c97be965ec3c" \
  -H "Content-Type: application/json" \
  -H 'X-Master-Key: $2a$10$6j4MIEVKRPTDxuwR3GRw2unUp8KZ3TbTvl/3psM5RA7nEpMZ8ALxO' \
  -d '{"imagenes": 0, "visitas": 0}'
```
