from fastapi import FastAPI, Request
from pydantic import BaseModel
import os
import requests
from langchain_community.vectorstores import FAISS
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain_community.embeddings import OpenAIEmbeddings
from langchain.chains import RetrievalQA
from dotenv import load_dotenv
from usuarios import (
    registrar_usuario,
    agregar_interaccion,
    actualizar_perfil_desde_respuesta,
    marcar_registro_confirmado,
    registro_ya_confirmado
)

# Cargar variables de entorno
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ULTRAMSG_TOKEN = os.getenv("ULTRAMSG_TOKEN")
ULTRAMSG_INSTANCE_ID = os.getenv("ULTRAMSG_INSTANCE_ID")

# Inicializar FastAPI
app = FastAPI()

# Cargar base vectorial
embedding_model = OpenAIEmbeddings(api_key=OPENAI_API_KEY)
vectorstore = FAISS.load_local("vectorstore_pyme", embedding_model, allow_dangerous_deserialization=True)

# Crear prompt personalizado
prompt_template = PromptTemplate(
    input_variables=["context", "question"],
    template="""
Eres un asistente especializado en asesorar a pequeñas y medianas empresas sobre convocatorias de ayudas públicas en España. 
Responde de forma clara, resumida y profesional en WhatsApp, utiliza emojis en el contexto de la conversación para que sea más amigable.
Inicialmene muestra información resumida y da más detalle cuando se te solicite.
Incluye el código BDNS y el título de la convocatoria si vas a mostrar varias. 
Si el usuario pide más información sobre alguna, puedes utilizar ese código para profundizar.
Solamente puedes responder a preguntas y comentarios relacionados con subvenciones, en caso de cualquier pregunta o comentario de otro tema debes decir que solo das información de subvenciones.
Solo debes saludar o decir Hola cuando te saluden, evitalo en el resto de la conversación.

{context}

Pregunta: {question}

Respuesta:
"""
)

# Crear modelo LLM
llm = ChatOpenAI(model="gpt-4o", openai_api_key=OPENAI_API_KEY, temperature=0)

# Crear RAG chain
rag_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=vectorstore.as_retriever(search_kwargs={"k": 50}),
    chain_type_kwargs={"prompt": prompt_template}
)

# Modelo de entrada
class WhatsAppMessage(BaseModel):
    from_: str  # Número del remitente
    message: str
    pushname: str  # Nombre desde UltraMsg

# Endpoint de recepción de mensajes
@app.post("/webhook")
async def receive_message(data: Request):
    try:
        payload = await data.json()
        wa_msg = WhatsAppMessage(
            from_=payload.get("data", {}).get("from"),
            message=payload.get("data", {}).get("body"),
            pushname=payload.get("data", {}).get("pushname", "")
        )

        numero_usuario = wa_msg.from_
        mensaje_usuario = wa_msg.message.strip()

        # Registrar usuario si es nuevo
        usuario = registrar_usuario(numero_usuario, nombre_whatsapp=wa_msg.pushname)

        if not registro_ya_confirmado(numero_usuario):
            if mensaje_usuario.lower() in ["no", "no gracias"]:
                send_whatsapp_message(numero_usuario, "✅ Perfecto, no se guardarán tus datos. ¿En qué te puedo ayudar?")
                marcar_registro_confirmado(numero_usuario)
                return {"status": "ok"}

            if mensaje_usuario.lower() in ["sí", "si"]:
                send_whatsapp_message(numero_usuario, "✍️ Por favor, dime tu ciudad y sector o interés, separados por coma. Ejemplo: Madrid, tecnología")
                return {"status": "ok"}

            if "," in mensaje_usuario:
                perfil = actualizar_perfil_desde_respuesta(numero_usuario, mensaje_usuario)
                marcar_registro_confirmado(numero_usuario)
                send_whatsapp_message(numero_usuario, f"✅ ¡Gracias {wa_msg.pushname or ''}! Tus datos fueron registrados: Ciudad: {perfil['ciudad']}, Interés: {perfil['interes']}.")
                return {"status": "ok"}

            send_whatsapp_message(numero_usuario, f"👋 ¡Hola {wa_msg.pushname or ''}! ¿Deseas registrar tus datos para recibir notificaciones? Responde con 'sí' o 'no'.")
            return {"status": "ok"}

        # Agregar interacciones
        agregar_interaccion(numero_usuario, f"Usuario: {mensaje_usuario}")
        historial = obtener_ultimos_mensajes(numero_usuario)

        respuesta = rag_chain.run(historial)

        agregar_interaccion(numero_usuario, f"Asistente: {respuesta}")
        send_whatsapp_message(numero_usuario, respuesta)

    except Exception as e:
        print(f"❌ Error procesando el mensaje: {e}")

    return {"status": "ok"}

# Obtener últimos mensajes del historial
def obtener_ultimos_mensajes(numero):
    from usuarios import RUTA_USUARIOS
    import json
    with open(RUTA_USUARIOS, encoding="utf-8") as f:
        data = json.load(f)
        return "\n".join(data.get(numero, {}).get("interacciones", [])[-10:])

# Enviar mensaje por UltraMsg
def send_whatsapp_message(to: str, message: str):
    url = f"https://api.ultramsg.com/{ULTRAMSG_INSTANCE_ID}/messages/chat"
    headers = {"Content-Type": "application/json"}
    payload = {
        "token": ULTRAMSG_TOKEN,
        "to": to,
        "body": message
    }
    requests.post(url, json=payload, headers=headers)
