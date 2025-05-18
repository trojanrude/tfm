import os
import json
import re
import requests
from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain_community.embeddings import OpenAIEmbeddings
from langchain.chains import RetrievalQA

# Cargar variables de entorno
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ULTRAMSG_TOKEN = os.getenv("ULTRAMSG_TOKEN")
ULTRAMSG_INSTANCE_ID = os.getenv("ULTRAMSG_INSTANCE_ID")

# Cargar usuarios
with open("usuarios.json", encoding="utf-8") as f:
    usuarios = json.load(f)

# Cargar base vectorial
embedding_model = OpenAIEmbeddings(api_key=OPENAI_API_KEY)
vectorstore = FAISS.load_local("vectorstore_pyme", embedding_model, allow_dangerous_deserialization=True)

# Crear modelo y prompt
llm = ChatOpenAI(model="gpt-4o", openai_api_key=OPENAI_API_KEY, temperature=0)
prompt_template = PromptTemplate(
    input_variables=["context", "question"],
    template="""
Eres un sistema de notificaciones automáticas que detecta subvenciones públicas en España.
Muestra solo las más relevantes para el sector/interés: "{question}" en formato breve de WhatsApp.

Incluye:
- Título de la subvención
- Código BDNS
- Presupuesto aproximado
- Enlace para más información

{context}
"""
)

rag_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=vectorstore.as_retriever(search_kwargs={"k": 5}),
    chain_type_kwargs={"prompt": prompt_template}
)

def extraer_codigos_bdns(texto):
    return re.findall(r"(?:BDNS)?[:\s]*([0-9]{5,})", texto, flags=re.IGNORECASE)

def send_whatsapp_message(to: str, message: str):
    url = f"https://api.ultramsg.com/{ULTRAMSG_INSTANCE_ID}/messages/chat"
    headers = {"Content-Type": "application/json"}
    payload = {
        "token": ULTRAMSG_TOKEN,
        "to": to,
        "body": message
    }
    requests.post(url, json=payload, headers=headers)

def enviar_notificaciones():
    cambios = False

    for numero, perfil in usuarios.items():
        print("\n\U0001F4CD Evaluando usuario:", numero)

        if not perfil.get("registro_confirmado"):
            print(" - Registro NO confirmado. Saltando...")
            continue

        ciudad = perfil.get("ciudad", "")
        interes = perfil.get("interes", "")
        nombre = perfil.get("nombre", "usuario")

        if not ciudad and not interes:
            print(" - Faltan datos de ciudad e interés. Saltando...")
            continue

        consulta = f"Subvenciones para {interes} en {ciudad}"
        print(" - Consulta generada:", consulta)

        respuesta = rag_chain.run(consulta)
        print("\n\U0001F50D Respuesta del modelo:\n", respuesta[:500])

        codigos_actuales = extraer_codigos_bdns(respuesta)
        print("\n\U0001F4CB Códigos BDNS extraídos:", codigos_actuales)

        codigos_previos = perfil.get("notificadas", [])
        nuevos = [c for c in codigos_actuales if c not in codigos_previos]
        print("\n\U0001F195 Nuevos códigos detectados:", nuevos)

        if nuevos:
            mensaje = f"\U0001F4E2 ¡Hola {nombre}! Hemos encontrado nuevas subvenciones que podrían interesarte:\n\n{respuesta}"
            send_whatsapp_message(numero, mensaje)
            perfil.setdefault("notificadas", []).extend(nuevos)
            cambios = True
        else:
            print(f"\n\u26A0️ No hay subvenciones nuevas para {nombre}.")

    if cambios:
        with open("usuarios.json", "w", encoding="utf-8") as f:
            json.dump(usuarios, f, indent=2, ensure_ascii=False)
        print("\n✅ Notificaciones enviadas y usuarios actualizados.")
    else:
        print("\n✅ No hay notificaciones nuevas para enviar.")

if __name__ == "__main__":
    enviar_notificaciones()
