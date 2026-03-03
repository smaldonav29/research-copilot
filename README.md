# 📚 Research Copilot — Academic Paper Assistant

Un asistente conversacional basado en IA para interactuar con una colección de 20 artículos académicos usando **Retrieval-Augmented Generation (RAG)** con OpenAI GPT-4o y ChromaDB.

---

## 🧠 Descripción

Research Copilot permite:

- Responder preguntas complejas sobre literatura académica.
- Recuperar pasajes relevantes de documentos.
- Proveer respuestas con **citas en formato APA**.
- Explorar los papers a través de una interfaz interactiva.
- Visualizar estadísticas de la colección de papers.

Este proyecto cumple con los requisitos de la Tarea 1 de la asignatura, implementando una arquitectura RAG completa con UI basada en Streamlit.

---

## 🏗️ Arquitectura del Sistema

User Query
│
▼
Streamlit UI (app/)
├── main.py (chat + UI)
├── pages/
│ ├── 2_Papers.py (Paper Browser)
│ └── 3_Analytics.py (Dashboard)
│
▼
Prompt Strategies (prompts/*.txt)
│
▼
RAG Pipeline (src/rag_pipeline.py)
├── Retriever (src/retrieval/)
├── Generator (src/generation/)
├── ChromaDB Vector Store (src/vectorstore/)
├── Embedding (src/embedding/)
└── Chunking (src/chunking/)
│
▼
papers/ (20 PDFs + paper_catalog.json)


---

## 🛠️ Requisitos

- Python 3.10+
- OpenAI API key
- Entorno virtual recomendado

---

## 🧰 Dependencias Principales

Las dependencias se especifican en `requirements.txt` e incluyen:

- openai
- tiktoken
- chromadb
- streamlit

Instálalas con:

```bash
pip install -r requirements.txt

## 🔐 Configuración de Variables de Entorno

Copia el archivo de ejemplo:

cp .env.example .env

Luego agrega tu OPENAI_API_KEY en .env.





