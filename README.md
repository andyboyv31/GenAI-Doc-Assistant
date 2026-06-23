# GenAI Document Assistant

## Overview

GenAI Document Assistant is a Generative AI-powered application that enables users to upload enterprise documents and ask natural language questions. The application uses Retrieval-Augmented Generation (RAG), ChromaDB, and Agent-Based Reasoning to retrieve relevant information and generate grounded responses.

## Features

* Multi-format document ingestion

  * PDF
  * TXT
  * CSV
  * Excel
  * JSON
  * YAML

* Semantic search using vector embeddings

* ChromaDB vector database

* Retrieval-Augmented Generation (RAG)

* Agent-Based Reasoning

* Output Verification

* Docker Deployment

## Architecture

User → FastAPI → Document Processing → Chunking → Embeddings → ChromaDB → Agents → Grounded Response

## Agent Workflow

User Question
→ Planner Agent
→ Retriever Agent
→ Reasoning Agent
→ Response Agent
→ Output Verification Agent
→ Final Response

## API Endpoints

* POST /Upload-Document
* GET /retrieve
* GET /rag-answer
* GET /agent-answer
* GET /health

## Deployment

### Docker

```bash
docker build -t genai-doc-assistant .
docker run -p 10000:10000 genai-doc-assistant
```

Access Swagger UI:

http://localhost:10000/docs

## Technologies

* Python
* FastAPI
* ChromaDB
* Sentence Transformers
* Docker
* GitHub

## Limitations

* Render free-tier memory limitations
* Mock LLM implementation
* No authentication mechanism

## Author

Andrew V
