"""Módulo de procesamiento de imágenes: EXIF, conversión y limpieza de nombres"""

import re
import io
import piexif


def limpiar_nombre(texto):
    texto = texto.lower().replace(" ", "_")
    texto = re.sub(r'[^\w\s-]', '', texto)
    return texto[:60].strip("_")


def agregar_exif(imagen, texto_alt):
    try:
        exif_dict = {"0th": {}, "Exif": {}}
        texto_bytes = texto_alt.encode('utf-8')
        exif_dict["0th"][piexif.ImageIFD.ImageDescription] = texto_bytes
        exif_dict["Exif"][piexif.ExifIFD.UserComment] = texto_bytes
        return piexif.dump(exif_dict)
    except:
        return None


def imagen_a_bytes(imagen, exif_bytes=None):
    buffer = io.BytesIO()
    if exif_bytes:
        imagen.save(buffer, format="JPEG", exif=exif_bytes, quality=95)
    else:
        imagen.save(buffer, format="JPEG", quality=95)
    buffer.seek(0)
    return buffer
