import os
import json
import requests

# Configuración
input_folder = "logs_divididos"
modelo = "llama3.1"
url = "http://localhost:11434/api/generate"

def analizar_log(path_archivo):
    with open(path_archivo, "r", encoding="utf-8") as f:
        logs_array = json.load(f)

    logs_str = json.dumps(logs_array, indent=2)

    prompt = f"""
Eres un analista de ciberseguridad. Analiza este log del WAF y responde:
- IP atacante
- Posible ataque 
- Payload con analisis
- Recomendaciones de prevencion

{logs_str}
"""

    data = {
        "model": modelo,
        "prompt": prompt,
        "stream": False
    }

    response = requests.post(url, json=data)
    if response.status_code == 200:
        result = response.json()
        return result["response"]
    else:
        print(f"Error {response.status_code} al procesar {path_archivo}")
        return None

def generar_analisis_global(respuestas):
    joined = "\n\n".join(f"[Bloque {i+1}]\n{r}" for i, r in enumerate(respuestas))
    
    prompt_final = f"""
Eres un analista senior de ciberseguridad. Has recibido análisis individuales de logs WAF procesados en bloques.
A continuación tienes los resúmenes de cada bloque. Crea un análisis global que incluya:
- Clasificación de los eventos (tipo de ataques, errores)
- Patrones comunes o repetidos entre bloques
- Enumera las IPs atacantes
- Evaluación del nivel de amenaza general
- Recomendaciones finales

{joined}
"""

    data = {
        "model": modelo,
        "prompt": prompt_final,
        "stream": False
    }

    response = requests.post(url, json=data)
    if response.status_code == 200:
        result = response.json()
        return result["response"]
    else:
        print(f"Error en el resumen global: {response.status_code}")
        return None

if __name__ == "__main__":
    archivos = sorted([
        os.path.join(input_folder, f)
        for f in os.listdir(input_folder)
        if f.endswith(".json")
    ])

    respuestas_individuales = []

    for idx, path in enumerate(archivos, start=1):
        print(f"\nAnalizando {os.path.basename(path)}...")
        respuesta = analizar_log(path)
        if respuesta:
            print(f"\nRespuesta del Bloque {idx}:\n{respuesta}\n" + "-" * 50)
            respuestas_individuales.append(respuesta)

    # Generar análisis final
    if respuestas_individuales:
        print("\nGenerando análisis final consolidado...\n")
        resumen_final = generar_analisis_global(respuestas_individuales)
        print("\nAnálisis final completo:\n")
        print(resumen_final)

        # Guardar en archivo
        with open("resumen_global_llama.txt", "w", encoding="utf-8") as f:
            f.write(resumen_final)
