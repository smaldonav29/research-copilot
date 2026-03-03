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

```
User Query
│
▼
Streamlit UI (app/)
├── main.py (chat + UI)
├── pages/
│   ├── 2_Papers.py (Paper Browser)
│   └── 3_Analytics.py (Dashboard)
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
```

---

## 🛠️ Requisitos

- Python 3.10+
- OpenAI API key
- Entorno virtual recomendado

---

## 🧰 Dependencias Principales

Las dependencias se especifican en `requirements.txt` e incluyen:

- `openai`
- `tiktoken`
- `chromadb`
- `streamlit`

Instálalas con:

```bash
pip install -r requirements.txt
```

---

## 🔐 Configuración de Variables de Entorno

Copia el archivo de ejemplo:

```bash
cp .env.example .env
```

Luego agrega tu `OPENAI_API_KEY` en `.env`.

---

## 🚀 Cómo Ejecutar

### 🔎 Indexar Papers (una sola vez)

Si aún no has indexado tus PDF (ingestión + embeddings):

```bash
python src/ingest.py
```

### 🧪 Ejecutar la Aplicación

```bash
streamlit run app/main.py
```

Abre el navegador y visita:

```
http://localhost:8501
```

---

## 💬 Uso

### 🧠 Chat / Q&A

Desde la UI principal puedes:

- Formular preguntas sobre tus papers.
- Seleccionar estrategia de prompt (v1–v4).
- Obtener respuestas académicas con citas APA.

### 📄 Paper Browser

Desde Paper Browser puedes:

- Ver la lista de tus 20 papers.
- Filtrar por título, autor, año o tema (topic).
- Explorar metadata y abstracts.

### 📊 Analytics Dashboard

Muestra estadísticas de tu colección:

- Número de papers por año.
- Distribución de topics.
- Conteo de autores.
- Tabla completa de información de los papers.

---

## 🧠 Estrategias de Prompt

| Versión | Archivo | Descripción |
|---------|---------|-------------|
| v1 | `v1_delimiters.txt` | Uso de delimitadores para estructurar el contexto |
| v2 | `v2_json_output.txt` | Salida estructurada en formato JSON |
| v3 | `v3_few_shot.txt` | Ejemplos few-shot para guiar las respuestas |
| v4 | `v4_chain_of_thought.txt` | Razonamiento paso a paso (chain-of-thought) |

---

## 📦 Estructura del Proyecto

```
research-copilot/
├── README.md
├── requirements.txt
├── .env.example
├── papers/
│   ├── paper_catalog.json
│   └── *.pdf
├── src/
│   ├── ingestion/
│   ├── chunking/
│   ├── embedding/
│   ├── vectorstore/
│   ├── retrieval/
│   ├── generation/
│   └── rag_pipeline.py
├── prompts/
│   ├── v1_delimiters.txt
│   ├── v2_json_output.txt
│   ├── v3_few_shot.txt
│   └── v4_chain_of_thought.txt
└── app/
    ├── main.py
    └── pages/
        ├── 2_Papers.py
        └── 3_Analytics.py
```

---

## ⚠️ Limitaciones Conocidas

- Tablas, figuras y fórmulas pueden perderse en la extracción de texto.
- PDFs escaneados no son soportados sin OCR previo.
- La calidad de las respuestas depende de los chunks indexados en Chroma.
- Si agregas nuevos papers, debes reindexar.

---

## 💡 Futuras Mejoras

- Gráficas más interactivas (Plotly o Altair).
- Seguimiento de uso de tokens por consulta.
- Exportar conversaciones a PDF o Markdown.
- Página Settings para configuración global del usuario.

---

## 📅 Autor

**Santiago Miguel Maldonado Vizcarra - Politólogo**  
Curso: Escuela de Verano QLab PUCP / Asignatura: Prompt Engineering 
Fecha de entrega: 2 de marzo del 2026
