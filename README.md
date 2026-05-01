# 🚀 DocuMind AI  
### AI-Powered Document Q&A (RAG System)

> Turn PDFs into an interactive knowledge base using LLMs and semantic search.

---

## 🖼️ Preview

### 📄 Upload
![Upload](./assets/upload.png)

### 💬 Chat
![Chat](./assets/chat.png)

### 📊 Response
![Response](./assets/response.png)

---

## ⚡ Features

- 📄 Chat with PDF documents  
- 🔍 Semantic search (vector embeddings)  
- 🧠 Context-aware answers (RAG)  
- 💬 Multi-turn conversation  
- ⚡ Fast API backend (FastAPI)  

---

## 🏗️ Architecture

```mermaid
flowchart LR
    A[PDF] --> B[Chunking]
    B --> C[Embeddings]
    C --> D[Vector DB]
    Q[Query] --> E[Search]
    D --> E
    E --> F[LLM]
    F --> G[Answer]
