import openai
import json
import os

# Usa variable de entorno por seguridad
openai.api_key = os.getenv("OPENAI_API_KEY")


# Carpeta con los logs divididos
input_folder = "logs_divididos"

def analizar_chunk(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        logs_chunk = json.load(f)
    logs_str = json.dumps(logs_chunk, indent=2)

    messages = [
        {
            "role": "system",
            "content": (
                "Eres un analista de ciberseguridad. Analiza este log del WAF y responde:\n"
                "- IP atacante\n"
                "- Posible ataque \n"
                "- Payload con analisis\n"
                "- Recomendaciones de prevencion\n"
            ),
        },
        {
            "role": "user",
            "content": f"Aquí están los logs:\n\n{logs_str}\n\nResume cualquier comportamiento malicioso."
        },
    ]

    print(f"Analizando {file_path}...")
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0.3,
    )
    return response.choices[0].message["content"]

def generar_resumen_global(respuestas):
    joined = "\n\n".join(
        f"[Bloque {i+1}]\n{resp}" for i, resp in enumerate(respuestas)
    )
    final_prompt = [
        {
            "role": "system",
            "content": "Eres un analista de seguridad. Resume múltiples análisis de logs de WAF y da una conclusión general.",
        },
        {
            "role": "user",
            "content": (
                "Estos son los análisis individuales por bloque:\n\n"
                f"{joined}\n\n"
                "Eres un analista senior de ciberseguridad. Has recibido análisis individuales de logs WAF procesados en bloques.\n"
                "A continuación tienes los resúmenes de cada bloque. Crea un análisis global que incluya:\n"
                "- Clasificación de los eventos (tipo de ataques, errores)\n"
                "- Patrones comunes o repetidos entre bloques\n"
                "- Enumera las IPs atacantes\n"
                "- Evaluación del nivel de amenaza general\n"
                "- Recomendaciones finales\n"
            ),
        },
    ]

    print("\nGenerando resumen global...")
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=final_prompt,
        temperature=0.3,
    )
    return response.choices[0].message["content"]

if __name__ == "__main__":
    respuestas = []

    for filename in sorted(os.listdir(input_folder)):
        if filename.endswith(".json"):
            path = os.path.join(input_folder, filename)
            respuesta = analizar_chunk(path)
            print(f"\nRespuesta para {filename}:\n{respuesta}\n{'-'*40}")
            respuestas.append(respuesta)

    resumen_final = generar_resumen_global(respuestas)
    print("\n===== ANÁLISIS FINAL =====\n")
    print(resumen_final)

    # Guardar resumen final (opcional)
    with open("resumen_global.txt", "w", encoding="utf-8") as f:
        f.write(resumen_final)
