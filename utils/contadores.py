"""Módulo de contadores: lectura y actualización de estadísticas en JSONBin"""

import requests

JSONBIN_BIN_ID = "6983d11b43b1c97be965ec3c"
JSONBIN_API_KEY = "$2a$10$6j4MIEVKRPTDxuwR3GRw2unUp8KZ3TbTvl/3psM5RA7nEpMZ8ALxO"


def obtener_contadores():
    """Obtiene los contadores actuales desde JSONbin"""
    try:
        url = f"https://api.jsonbin.io/v3/b/{JSONBIN_BIN_ID}/latest"
        headers = {"X-Master-Key": JSONBIN_API_KEY}
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            return response.json()["record"]
        return {"imagenes": 0, "visitas": 0}
    except:
        return {"imagenes": 0, "visitas": 0}


def actualizar_contadores(imagenes=0, visitas=0):
    """Incrementa los contadores en JSONbin"""
    try:
        datos = obtener_contadores()
        datos["imagenes"] = datos.get("imagenes", 0) + imagenes
        datos["visitas"] = datos.get("visitas", 0) + visitas

        url = f"https://api.jsonbin.io/v3/b/{JSONBIN_BIN_ID}"
        headers = {
            "Content-Type": "application/json",
            "X-Master-Key": JSONBIN_API_KEY
        }
        requests.put(url, json=datos, headers=headers, timeout=5)
        return datos
    except:
        return {"imagenes": 0, "visitas": 0}
