# LOG DE ESTADO - GaryText Pro

**Fecha:** 12 de febrero de 2026
**Repositorio:** https://github.com/GaryMp/Generador-de-altext-para-imagenes

---

## Resumen de lo implementado

### 1. Migración a Google Gemini API
- **Antes:** Modelo BLIP local (Salesforce/blip-image-captioning-base) - lento (~10-15s/imagen)
- **Ahora:** Google Gemini 2.5 Flash Lite (`gemini-2.5-flash-lite`) - rápido (~2-4s/imagen)
- API Key configurada en `st.secrets["GEMINI_API_KEY"]`
- Tier gratuito con facturación activa (15 RPM)

### 2. Manejo de Rate Limit
- Delay de 1 segundo antes de cada imagen
- Sistema de reintentos automáticos (2 intentos, 4s espera en error 429)
- Modelo cacheado con `@st.cache_resource` para mejor rendimiento
- Procesamiento secuencial imagen por imagen con feedback entre cada una

### 3. Prompt Estructurado (Nombre + Descripción)
El prompt pide a Gemini dos campos separados:
```
NOMBRE: 3-5 palabras claras y significativas → nombre_archivo.jpg
DESCRIPCION: 15-25 palabras detalladas → texto alternativo
```

**Reglas del prompt:**
- Evita: "Es una", "En esta imagen", "Se muestra", "Se ve", "Hay un/una"
- Empieza directamente con el sujeto principal
- Español estándar neutro (sin regionalismos)
- Limpieza automática de prefijos genéricos con regex (`_PREFIJOS_ES`, `_PREFIJOS_EN`)

### 4. Soporte Bilingüe (Español / Inglés)
- Opción en "Opciones avanzadas" para elegir idioma del texto alternativo
- Prompts separados para cada idioma
- Limpieza de prefijos adaptada por idioma

### 5. Edición y Descarga de Resultados
- **Texto editable:** cada resultado tiene un `text_area` para modificar la descripción antes de descargar
- **Descarga individual:** botón por cada imagen procesada (JPEG con EXIF actualizado)
- **Descarga ZIP:** cuando hay múltiples imágenes, botón para descargar todas en ZIP
- **Botón "Quitar":** eliminar resultados individuales
- **Botón "Limpiar todo":** reiniciar para procesar nuevas imágenes
- **Metadatos EXIF opcionales:** opción para guardar o no la descripción en EXIF (ImageDescription + UserComment)

### 6. Contador de Visitas y Estadísticas
- `st.components.v1.html()` para ejecutar JS en iframe (no funciona con `st.markdown`)
- LocalStorage para identificar visitantes únicos
- Contadores almacenados en JSONBin (visitas + imágenes analizadas)
- Credenciales JSONBin migradas a `st.secrets` (ya no hardcodeadas)

### 7. Accesibilidad WCAG 2.2 AA
- `lang="es"` inyectado en el `<html>` vía JS para screen readers (WCAG 3.1.1)
- Focus outline de 3px en todos los elementos interactivos
- Targets mínimos de 44x44px en botones (WCAG 2.5.8)
- Clase `.sr-only` para texto invisible accesible a lectores de pantalla
- Iframes de utilidad ocultos con `aria-hidden="true"` y `tabIndex=-1`
- Iconos decorativos marcados con `aria-hidden="true"`
- Ocultar chrome de Streamlit (menú, header, toolbar, deploy button)
- Optimizado para NVDA y JAWS

### 8. Estilo Visual Rasta
- Borde superior degradado (verde-amarillo-rojo) de 4px
- Animación de borde durante procesamiento (degradado en movimiento)
- Título "Gary" con cada letra coloreada (G=verde, a=dorado, r=rojo, y=verde)
- Separadores horizontales con degradado rasta
- Footer con banda de color rasta

### 9. Tema Claro Forzado
- CSS que fuerza `background-color: #ffffff` en contenedores, expanders, selectbox, text areas, file uploader
- Texto forzado a `#1a1a1a` en todos los componentes
- Evita problemas con usuarios en modo oscuro

### 10. Diseño Responsive Móvil
- Media queries para pantallas < 640px
- Columnas se apilan verticalmente en móvil
- Botones y textos con tamaño adaptado
- Thumbnails centrados
- Footer con texto más compacto

### 11. Botón de Donación Ko-fi
- URL: https://ko-fi.com/garydev
- Ubicación: Footer de la app

---

## Arquitectura del Proyecto

```
├── streamlit_app.py              # Interfaz principal (Streamlit)
├── utils/
│   ├── __init__.py
│   ├── gemini.py                 # IA: config Gemini, prompt, reintentos, limpieza de prefijos
│   ├── imagen.py                 # Procesamiento: EXIF, conversión a bytes, limpieza de nombres
│   ├── contadores.py             # Estadísticas: lectura/escritura en JSONBin
│   └── estilos.py                # CSS WCAG 2.2 AA + responsive + tema rasta
├── .streamlit/
│   ├── config.toml               # Config Streamlit (toolbarMode: minimal)
│   └── secrets.toml.example      # Ejemplo de secrets
├── requirements.txt              # Dependencias Python
├── LOG_ESTADO.md                 # Este archivo
└── .gitignore
```

---

## Configuración

Todas las credenciales van en `.streamlit/secrets.toml`:

```toml
GEMINI_API_KEY = "tu-api-key-gemini"
JSONBIN_BIN_ID = "tu-bin-id"
JSONBIN_API_KEY = "tu-api-key-jsonbin"
```

- **Gemini API Key:** https://aistudio.google.com/
- **JSONBin:** https://jsonbin.io/
- **Streamlit Cloud:** Settings → Secrets (mismo formato TOML)

---

## Pendientes / Ideas Futuras
- [ ] Cuadro de preguntas adicionales por imagen analizada
- [ ] Botones de compartir en redes sociales
- [ ] Sección de testimonios

---

## Problemas Conocidos y Soluciones

| Problema | Solución |
|----------|----------|
| JavaScript no se ejecuta en st.markdown | Usar `components.html()` |
| Error 429 rate limit | Delays + reintentos automáticos |
| Primera imagen falla | Delay de 1s antes de cada request |
| Modelo lento al cargar | Cache con `@st.cache_resource` |
| Modo oscuro rompe estilos | CSS forzando tema claro en todos los componentes |
| Screen readers leen chrome de Streamlit | CSS `display:none` en elementos no relevantes |

---

## Comandos Útiles
```bash
# Levantar en local
source venv/Scripts/activate
streamlit run streamlit_app.py

# Ver cambios locales
git status

# Subir cambios
git add .
git commit -m "Descripción del cambio"
git push

# Resetear contadores a 0
curl -X PUT "https://api.jsonbin.io/v3/b/TU_BIN_ID" \
  -H "Content-Type: application/json" \
  -H 'X-Master-Key: TU_API_KEY' \
  -d '{"imagenes": 0, "visitas": 0}'
```
