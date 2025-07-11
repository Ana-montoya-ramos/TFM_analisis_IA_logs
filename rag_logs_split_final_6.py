# rag_logs_split_final.py

# Importación de librerías necesarias
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain_community.llms import Ollama
from langchain.chains import RetrievalQA

import os
import json


def load_pdf(file_path: str):
    loader = PyPDFLoader(file_path)
    pages = loader.load_and_split()
    print(f"Documento cargado: {len(pages)} páginas.")
    return pages


def split_text(pages, chunk_size=1000, chunk_overlap=100):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )
    texts = splitter.split_documents(pages)
    print(f"Documento dividido en {len(texts)} fragmentos.")
    return texts


def create_vector_store(texts):
    embedding_model = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    vector_store = FAISS.from_documents(texts, embedding_model)
    print("Base de vectores FAISS creada.")
    return vector_store


def load_llm():
    return Ollama(model="llama3.1")


def build_rag_chain(vector_store, llm):
    retriever = vector_store.as_retriever(search_type="similarity", search_kwargs={"k": 4})
    qa_chain = RetrievalQA.from_chain_type(llm=llm, retriever=retriever)
    print("Cadena RAG lista para responder preguntas.")
    return qa_chain


def ask_question(chain, query, bloque_id=None):
    if bloque_id is not None:
        print(f"\nAnalizando bloque {bloque_id}...")
    else:
        print(f"\nAnalizando pregunta completa...")
    response = chain.run(query)
    print(f"Respuesta:\n{response}\n")
    return response


def leer_archivos_logs_en_carpeta(carpeta_logs):
    archivos = sorted([
        os.path.join(carpeta_logs, f)
        for f in os.listdir(carpeta_logs)
        if f.endswith(".json")
    ])
    print(f"Se encontraron {len(archivos)} archivos de logs en '{carpeta_logs}'.")
    return archivos


def leer_eventos_de_archivo(path_archivo):
    with open(path_archivo, 'r', encoding='utf-8') as f:
        eventos = json.load(f)
    print(f"{len(eventos)} eventos leídos de '{os.path.basename(path_archivo)}'.")
    return eventos


def generar_pregunta_desde_eventos(eventos_bloque):
    texto_json = json.dumps(eventos_bloque, indent=2, ensure_ascii=False)
    prompt = (
        "Eres un analista de ciberseguridad. Analiza este log del WAF y responde:\n"
        "- IP atacante\n"
        "- Posible ataque \n"
        "- Payload con analisis\n"
        "- Recomendaciones de prevencion\n"
        f"{texto_json}"
    )
    return prompt


def generar_resumen_final(respuestas_por_bloque):
    texto_completo = "\n\n".join(
        [f"[Bloque {i+1}]\n{resp}" for i, resp in enumerate(respuestas_por_bloque)]
    )
    prompt = (
        "Eres un analista senior de ciberseguridad. Has recibido análisis individuales de logs WAF procesados en bloques.\n"
        "A continuación tienes los resúmenes de cada bloque. Crea un análisis global que incluya:\n"
        "- Clasificación de los eventos (tipo de ataques, errores)\n"
        "- Patrones comunes o repetidos entre bloques\n"
        "- Enumera las IPs atacantes\n"
        "- Evaluación del nivel de amenaza general\n"
        "- Recomendaciones finales\n"
        f"{texto_completo}"
    )
    return prompt


if __name__ == "__main__":
    pdf_path = "document.pdf"
    carpeta_logs = "logs_divididos"

    # Procesar el documento base
    pages = load_pdf(pdf_path)
    texts = split_text(pages)
    vector_store = create_vector_store(texts)

    # Cargar modelo desde Ollama
    llm = load_llm()

    # Construir RAG
    rag_chain = build_rag_chain(vector_store, llm)

    # Leer logs por bloques y analizar
    archivos_logs = leer_archivos_logs_en_carpeta(carpeta_logs)
    respuestas_parciales = []

    for idx, path_log in enumerate(archivos_logs, start=1):
        eventos = leer_eventos_de_archivo(path_log)
        pregunta = generar_pregunta_desde_eventos(eventos)
        respuesta = ask_question(rag_chain, pregunta, bloque_id=idx)
        respuestas_parciales.append(respuesta)

    # Generar análisis final
    pregunta_final = generar_resumen_final(respuestas_parciales)
    print("\n----- Generando análisis final de todos los bloques -----")
    respuesta_final = ask_question(rag_chain, pregunta_final)
    print("Análisis final completo:\n", respuesta_final)
