import json
import os
from pathlib import Path
from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings

# Cargar variables de entorno
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Cargar datos desde JSON
ruta_json = Path("convocatorias_pyme.json")
with open(ruta_json, encoding="utf-8") as f:
    datos = json.load(f)

# Crear lista de documentos
documentos = []
for subvencion in datos:
    campos = {
        "Título": subvencion.get("descripcion"),
        "Finalidad": subvencion.get("descripcionFinalidad"),
        "Bases Reguladoras": subvencion.get("descripcionBasesReguladoras"),
        "Presupuesto": subvencion.get("presupuestoTotal"),
        "Órgano convocante": subvencion.get("organo", {}).get("nivel2"),
        "Código BDNS": subvencion.get("codigoBDNS"),
        "Fecha de Recepción": subvencion.get("fechaRecepcion"),
        "Inicio de Solicitud": subvencion.get("fechaInicioSolicitud"),
        "Fin de Solicitud": subvencion.get("fechaFinSolicitud"),
        "URL Bases Reguladoras": subvencion.get("urlBasesReguladoras")
    }

    contenido = "\n".join(f"{k}: {v}" for k, v in campos.items() if v)

    documentos.append(Document(page_content=contenido, metadata={"id": subvencion.get("id")}))

print(f"✅ Documentos listos para indexar: {len(documentos)}")

# Crear embeddings y guardar base vectorial
embedding_model = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
vectorstore = FAISS.from_documents(documentos, embedding_model)
vectorstore.save_local("vectorstore_pyme")
print("✅ Vectorstore guardado correctamente.")
