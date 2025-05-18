import json
from pathlib import Path

RUTA_USUARIOS = Path("usuarios.json")

# Inicializar archivo si no existe
if not RUTA_USUARIOS.exists():
    RUTA_USUARIOS.write_text("{}", encoding="utf-8")


def cargar_datos():
    with open(RUTA_USUARIOS, encoding="utf-8") as f:
        return json.load(f)


def guardar_datos(data):
    with open(RUTA_USUARIOS, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def registrar_usuario(numero, nombre_whatsapp=""):
    data = cargar_datos()
    if numero not in data:
        data[numero] = {
            "nombre": nombre_whatsapp or "Desconocido",
            "ciudad": None,
            "interes": None,
            "registro_confirmado": False,
            "interacciones": []
        }
        guardar_datos(data)
    return data[numero]


def agregar_interaccion(numero, texto):
    data = cargar_datos()
    if numero in data:
        data[numero]["interacciones"].append(texto)
        guardar_datos(data)


def actualizar_perfil_desde_respuesta(numero, texto):
    data = cargar_datos()
    partes = [p.strip() for p in texto.split(",")]
    ciudad = partes[0] if len(partes) > 0 else None
    interes = partes[1] if len(partes) > 1 else None

    if numero in data:
        data[numero]["ciudad"] = ciudad
        data[numero]["interes"] = interes
        guardar_datos(data)
        return {"ciudad": ciudad, "interes": interes}
    return None


def marcar_registro_confirmado(numero):
    data = cargar_datos()
    if numero in data:
        data[numero]["registro_confirmado"] = True
        guardar_datos(data)


def registro_ya_confirmado(numero):
    data = cargar_datos()
    return data.get(numero, {}).get("registro_confirmado", False)
