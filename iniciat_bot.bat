@echo off
title Bot RAG + UltraMsg

:: Iniciar FastAPI en una nueva terminal
start cmd /k "C:\Users\pipol\anaconda3\Scripts\activate.bat tfm && cd /d C:\Users\pipol\data && uvicorn main:app --reload"

:: Esperar a que FastAPI arranque
timeout /t 5

:: Iniciar ngrok y guardar la salida en un log
cd /d C:\ngrok
start cmd /k "ngrok http 8000 --log=stdout > ngrok_log.txt"
