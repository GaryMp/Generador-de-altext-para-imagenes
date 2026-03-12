"""Módulo de contadores: lectura y actualización de estadísticas en JSONBin"""

import streamlit as st
import requests

JSONBIN_BIN_ID = st.secrets.get("JSONBIN_BIN_ID", "")
JSONBIN_API_KEY = st.secrets.get("JSONBIN_API_KEY", "")


@st.cache_data(ttl=60)
def obtener_contadores():
    """Obtiene los contadores actuales desde JSONbin. Cacheado 60s para no bloquear el render."""
    try:
        url = f"https://api.jsonbin.io/v3/b/{JSONBIN_BIN_ID}/latest"
        headers = {"X-Master-Key": JSONBIN_API_KEY}
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            return response.json()["record"]
        return {"imagenes": 0, "visitas": 0}
    except:
        return {"imagenes": 0, "visitas": 0}


def actualizar_contadores(imagenes=0, visitas=0, datos_actuales=None):
    """Incrementa los contadores en JSONbin. Usa datos_actuales si están disponibles
    para evitar un GET extra."""
    try:
        datos = dict(datos_actuales) if datos_actuales else obtener_contadores()
        datos["imagenes"] = datos.get("imagenes", 0) + imagenes
        datos["visitas"] = datos.get("visitas", 0) + visitas

        url = f"https://api.jsonbin.io/v3/b/{JSONBIN_BIN_ID}"
        headers = {
            "Content-Type": "application/json",
            "X-Master-Key": JSONBIN_API_KEY
        }
        requests.put(url, json=datos, headers=headers, timeout=5)
        obtener_contadores.clear()  # invalidar caché tras actualizar
        return datos
    except:
        return {"imagenes": 0, "visitas": 0}
