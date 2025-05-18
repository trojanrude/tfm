# Subvenciones WhatsApp Bot – Asistente conversacional con RAG

Este proyecto implementa un bot conversacional inteligente que permite consultar subvenciones públicas para PYMEs y autónomos en España a través de WhatsApp. Utiliza una arquitectura de generación aumentada por recuperación (RAG) para ofrecer respuestas personalizadas basadas en convocatorias reales extraídas desde la API de InfoSubvenciones.

## ¿Qué hace?

- Extrae subvenciones desde fuentes oficiales.
- Representa la información como vectores semánticos usando embeddings de OpenAI.
- Permite hacer preguntas en lenguaje natural sobre ayudas y convocatorias.
- Entrega respuestas conversacionales por WhatsApp vía UltraMsg.
- Envía notificaciones automáticas cuando hay subvenciones nuevas que coinciden con tu perfil.

## Tecnologías utilizadas

- FastAPI – Framework backend para el webhook conversacional.
- LangChain – Conexión entre modelos LLM y datos estructurados.
- FAISS – Base vectorial para recuperación semántica.
- OpenAI – Embeddings y modelo generativo (gpt-4o).
- UltraMsg – API REST para integrar WhatsApp.
- Ngrok – Túnel local para exponer el servidor en pruebas.

## Estructura del repositorio
```bash
tfm/
├── data/                       # Datos JSON descargados (subvenciones y usuarios anonimizados)
├── vectorstore_pyme/          # Índice FAISS con subvenciones embebidas
├── main.py                    # Webhook vía FastAPI
├── notificaciones.py          # Envío automático de alertas por WhatsApp
├── extraccion_subvenciones.py # Descarga de subvenciones desde API oficial
├── generar_vectorstore.py     # Indexación semántica de documentos
├── usuarios.py                # Gestión de usuarios y perfiles
├── .env.example               # Variables de entorno (plantilla)
├── requirements.txt           # Dependencias del proyecto
└── README.md                  # Esta documentación
```

## Cómo ejecutar el proyecto

### 1. Clonar el repositorio

git clone https://github.com/trojanrude/tfm.git
cd tfm

### 2. Crear entorno virtual e instalar dependencias

python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
pip install -r requirements.txt

### 3. Configurar archivo .env

cp .env.example .env

Edita .env y añade tus claves de OpenAI y UltraMsg.

### 4. Ejecutar webhook local

uvicorn main:app --reload

Usa Ngrok para exponer el webhook:

ngrok http 8000

Copia la URL pública generada (ej. https://xxxx.ngrok-free.app/webhook) y configúrala en tu cuenta de UltraMsg.

### 5. Otros scripts útiles

# Extraer subvenciones
python extraccion_subvenciones.py

# Generar vectorstore (FAISS)
python generar_vectorstore.py

# Enviar notificaciones automáticas
python notificaciones.py

## Variables de entorno requeridas

Edita el archivo .env con las siguientes variables:

OPENAI_API_KEY=tu_clave_openai
ULTRAMSG_TOKEN=tu_token_ultramsg
ULTRAMSG_INSTANCE_ID=tu_instance_id_ultramsg

## Licencia

Este proyecto se distribuye bajo licencia MIT. Puedes utilizarlo, modificarlo y adaptarlo libremente.

## Créditos

Desarrollado como Trabajo Final del Máster en Ciencia de Datos.
Autor: Luis Felipe Sánchez Gutierrez
Contacto: lfsanchezgutierrez@uoc.edu
