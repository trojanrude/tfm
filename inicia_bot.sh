#!/bin/bash

# Activar entorno virtual (modificar 'venv' si el entorno tiene otro nombre)
if [ -d "venv" ]; then
  source venv/bin/activate
fi

# Cargar variables desde archivo .env (si existe)
# Se debe modificar el nombre del archivo si tu .env se llama distinto
export $(grep -v '^#' .env 2>/dev/null | xargs)

# Ejecutar la API FastAPI con uvicorn
# Hay que asegurarse de que 'main.py' tenga un objeto llamado 'app'
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
