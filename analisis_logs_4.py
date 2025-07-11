import requests
import json


with open("logs/waf_logs_array.json", "r", encoding="utf-8") as f:
    logs_array = json.load(f)


logs_str = json.dumps(logs_array, indent=2)


prompt = f"""Eres un analista de ciberseguridad. Analiza estos logs del WAF con un resumen claro:\n"
    "- IPs frecuentes\n"
    "- Posibles ataques o patrones\n"
    "- Recomendaciones si las hay\n\n"
    "- Clasifica todos logs segun si es ataque, solicitud legitima o error y muestralo en formato json con sus caracteristicas"
    {logs_str}
    """
url = "http://localhost:11434/api/generate"
data = {
    "model": "llama3.1",
    "prompt": prompt,
    "stream": False
}


response = requests.post(url, json=data)


if response.status_code == 200:
    result = response.json()
    print("\n Analisis generado por LLaMA 3.1:\n")
    print(result["response"])


print(f"Error {response.status_code}: {response.text}")
