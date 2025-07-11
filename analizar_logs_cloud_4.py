import openai
import json
import os


# Introducir la API key de openAI en la terminal como variable global

# Archivo grande con todos los logs
input_file = "logs/waf_logs_array.json"


# Carpeta para guardar los archivos divididos
output_folder = "logs_divididos"
os.makedirs(output_folder, exist_ok=True)


# Tamaño del chunk (número de eventos por archivo pequeño)
chunk_size = 2


def dividir_json(input_path, output_dir, chunk_size):
    with open(input_path, "r", encoding="utf-8") as f:
        logs = json.load(f)


    for i in range(0, len(logs), chunk_size):
        chunk = logs[i:i+chunk_size]
        chunk_file = os.path.join(output_dir, f"chunk_{i//chunk_size + 1}.json")
        with open(chunk_file, "w", encoding="utf-8") as cf:
            json.dump(chunk, cf, indent=2)
        print(f"Guardado {chunk_file} con {len(chunk)} eventos")


def enviar_chunk(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        logs_chunk = json.load(f)
    logs_str = json.dumps(logs_chunk, indent=2)


    messages = [
        {
            "role": "system",
            "content": (
                "Eres un experto en ciberseguridad. Analiza logs de un WAF y explica patrones sospechosos. "
                "Analiza estos logs del WAF. Responde con un resumen claro de:\n"
                "- IPs frecuentes\n- Posibles ataques o patrones\n- Recomendaciones si las hay\n\n"
            ),
        },
        {
            "role": "user",
            "content": f"Aquí están los logs:\n\n{logs_str}\n\nResume cualquier comportamiento malicioso."
        },
    ]


    print(f"Enviando {file_path}...")
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0.3,
    )
    return response.choices[0].message["content"]


if __name__ == "__main__":
    dividir_json(input_file, output_folder, chunk_size)


    respuestas = []
    for filename in sorted(os.listdir(output_folder)):
        if filename.endswith(".json"):
            path = os.path.join(output_folder, filename)
            resultado = enviar_chunk(path)
            print(f"\nRespuesta para {filename}:\n{resultado}\n{'-'*40}\n")
            respuestas.append(resultado)