from fastapi import FastAPI, Request
import os
import json


app = FastAPI()
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)


@app.post("/logs")
async def receive_logs(request: Request):
    data = await request.json()
    # data es una lista JSON aquí


    with open(os.path.join(LOG_DIR, "waf_logs_array.json"), "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


    return {"status": "ok", "message": f"Recibidos {len(data)} eventos"}