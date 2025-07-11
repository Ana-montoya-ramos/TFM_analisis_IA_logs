import json
import os

# Configuración
input_file = "logs/waf_logs_array.json"
output_folder = "logs_divididos"
chunk_size = 1  # Número de eventos por archivo

def dividir_json(input_path, output_dir, chunk_size):
    with open(input_path, "r", encoding="utf-8") as f:
        logs = json.load(f)

    os.makedirs(output_dir, exist_ok=True)

    for i in range(0, len(logs), chunk_size):
        chunk = logs[i:i+chunk_size]
        chunk_file = os.path.join(output_dir, f"chunk_{i//chunk_size + 1}.json")
        with open(chunk_file, "w", encoding="utf-8") as cf:
            json.dump(chunk, cf, indent=2)
        print(f"Guardado {chunk_file} con {len(chunk)} eventos")

if __name__ == "__main__":
    dividir_json(input_file, output_folder, chunk_size)
