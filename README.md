# Air-Gapped Agentic AI Workbench (SIH 26117)

Welcome to the team repository! This project implements a sovereign, air-gapped AI workbench running locally on host hardware and broadcasting via LAN for collaborative development.

---

## 🏗️ Architecture & Infrastructure
- **Host Machine:** Laptop running NVIDIA RTX 3050 (handling core LLM inference via Ollama/llama-server).
- **Network Host IP:** `http://192.168.10.190:11434`
- **Backend Framework:** FastAPI (Python)
- **Local Database/RAG:** ChromaDB + Nomic Embeddings

---

## 👥 Module Ownership (Task Breakdown)
1. **Developer 1 (FastAPI & Gateway):** Main entrypoint (`backend/main.py`), CORS configuration, and route aggregations.
2. **Developer 2 (Core Inference):** Ollama client wrappers (`backend/core/ollama_client.py`) and prompt templates.
3. **Developer 3 (RAG Pipeline):** Document parsing, text chunking, and ChromaDB integration (`backend/rag/`).
4. **Developer 4 (Sandbox & Tools):** Secure code execution subprocessing and report file generators (`backend/sandbox/`).
5. **Developer 5 (Trust Layer):** Grounding checks, fact-verification logic, and hallucination reduction (`backend/trust_layer/`).
6. **Developer 6 (Frontend UI):** Chat interface, file uploaders, and connection service pointing to the host LAN IP (`frontend/`).

---

## 🚀 Quick Start Guide for Teammates

### 1. Clone the Repository
```bash
git clone <your-repository-url>
cd air-gapped-ai-workbench

## Author

Saieshwar Gujjeti