# LOG DE ESTADO - GaryText Pro

**Fecha:** 4 de febrero de 2026
**Repositorio:** https://github.com/GaryMp/Generador-de-altext-para-imagenes

---

## Resumen de lo implementado

### 1. Estilo visual con colores Rasta
- Borde superior degradado (verde-amarillo-rojo) de 4px
- Título "Gary" con cada letra coloreada (G=verde, a=amarillo, r=rojo, y=verde)
- Separadores horizontales con degradado rasta (opacidad 0.6)
- Footer con banda de color rasta

### 2. Corrección de tema claro forzado
- Problema: usuarios con modo oscuro veían fondo negro + texto negro
- Solución: CSS que fuerza `background-color: #ffffff` en `.stApp` y contenedores principales

### 3. Integración JSONBin.io para contadores
**Configuración:**
```
JSONBIN_BIN_ID = "6983d11b43b1c97be965ec3c"
JSONBIN_API_KEY = "$2a$10$6j4MIEVKRPTDxuwR3GRw2unUp8KZ3TbTvl/3psM5RA7nEpMZ8ALxO"
```

**Estructura del JSON:**
```json
{
  "imagenes": 0,
  "visitas": 0
}
```

**Funciones Python:**
- `obtener_contadores()` - GET al bin, retorna dict con valores actuales
- `actualizar_contadores(imagenes=0, visitas=0)` - PUT para incrementar valores

**Nota:** Las credenciales están directamente en el código. Para mayor seguridad, se podría migrar a `st.secrets` en el futuro.

### 4. Lógica de LocalStorage para visitas únicas
**Problema:** `st.session_state` se reinicia al refrescar la página, causando que cada refresh cuente como nueva visita.

**Solución:** JavaScript que usa `localStorage` del navegador.

**Flujo:**
1. Al cargar, verifica si existe `localStorage.getItem("garytext_visitado")`
2. Si NO existe:
   - Guarda marca: `localStorage.setItem("garytext_visitado", timestamp)`
   - Llama a JSONBin para incrementar visitas
   - Actualiza el contador en pantalla
3. Si existe: no hace nada

**Resultado:** Solo cuenta visitantes únicos, persiste aunque refresque o cierre el navegador.

### 5. Botón de donación Ko-fi
**URL:** https://ko-fi.com/garydev

**Ubicación:** Footer de la app

**Elementos:**
- Mensaje: "Si te ha parecido útil esta aplicación, no dudes en donarme un café"
- Botón oficial: imagen de Ko-fi (`https://storage.ko-fi.com/cdn/kofi2.png?v=3`)

---

## Archivos modificados
- `streamlit_app.py` - Código principal con todas las funcionalidades
- `requirements.txt` - Agregado `requests` para llamadas a JSONBin
- `.gitignore` - Excluye archivos innecesarios

---

## Pendientes / Ideas futuras
- [ ] Migrar credenciales de JSONBin a `st.secrets`
- [ ] Botones de compartir en redes sociales
- [ ] Sección de testimonios
- [ ] Copiar texto al portapapeles
- [ ] Previsualización de imágenes
- [ ] Exportar como HTML/CSV

---

## Comandos útiles
```bash
# Ver cambios locales
git status

# Subir cambios
git add .
git commit -m "Descripción del cambio"
git push

# La app se actualiza automáticamente en Streamlit Cloud (1-2 min)
```
