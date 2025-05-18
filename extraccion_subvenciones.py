import requests
import json
from time import sleep

# 🔍 Paso 1: Buscar convocatorias por palabra clave
def buscar_convocatorias(descripcion="PYME", cantidad=50):
    url = "https://www.infosubvenciones.es/bdnstrans/api/convocatorias/busqueda"
    params = {
        "vpd": "GE",
        "descripcion": descripcion,
        "descripcionTipoBusqueda": 1,
        "page": 0,
        "pageSize": cantidad,
        "order": "numeroConvocatoria",
        "direccion": "desc"
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json().get("content", [])

# 📄 Paso 2: Obtener detalle completo de una convocatoria
def obtener_detalle_convocatoria(num_conv):
    url = "https://www.infosubvenciones.es/bdnstrans/api/convocatorias"
    params = {
        "numConv": num_conv,
        "vpd": "GE"
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()

# ▶️ Ejecución principal
if __name__ == "__main__":
    print("🔍 Buscando convocatorias que contengan 'PYME'...\n")
    resultados = []

    try:
        convocatorias = buscar_convocatorias(cantidad=50)
        for c in convocatorias:
            num = c.get("numeroConvocatoria")
            print(f"📄 Descargando detalle de convocatoria {num}...")
            detalle = obtener_detalle_convocatoria(num)
            resultados.append(detalle)
            sleep(0.3)

        # Guardar todo el JSON completo
        with open("convocatorias_pyme.json", "w", encoding="utf-8") as f:
            json.dump(resultados, f, indent=2, ensure_ascii=False)

        print(f"\n✅ Archivo 'convocatorias_pyme.json' generado con éxito con {len(resultados)} convocatorias.")
    except Exception as e:
        print(f"\n❌ Error: {e}")
