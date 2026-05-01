# DocuMind-AI
A full-stack AI-powered application for intelligent PDF question-answering using RAG (Retrieval Augmented Generation) technology.

## 🚀 Quick Start

### Prerequisites
- Node.js (v16+)
- Python 3.8+
- OpenAI API Key

### Installation & Setup

1. **Backend Setup**
```bash
cd backend
pip install -r requirements.txt
```

Create `.env` file in backend directory:
```
OPENAI_API_KEY=your_openai_api_key_here
```

Start backend:
```bash
uvicorn main:app --reload --port 8000
```

2. **Frontend Setup**
```bash
cd frontend
npm install
npm run dev
```


## 📁 Project Structure

```
pdf-rag-app/
├── backend/                 # FastAPI Backend
│   ├── main.py             # Main application
│   ├── routes/             # API routes
│   ├── services/           # Business logic
│   ├── storage/            # Vector database storage
│   └── requirements.txt    # Python dependencies
│
└── frontend/               # React Frontend
    ├── src/
    │   ├── components/     # React components
    │   ├── App.jsx         # Main app component
    │   └── index.css       # Global styles
    ├── package.json
    └── vite.config.js
```

## ✨ Features

- 📄 PDF Upload with drag-and-drop
- 🤖 AI-powered question answering
- 💬 Real-time streaming responses
- 🎨 Modern, gradient-based UI
- 📱 Fully responsive design
- ⚡ Fast vector search with FAISS

## 🛠️ Tech Stack

**Frontend:**
- React 18
- Vite
- Framer Motion
- Lucide Icons

**Backend:**
- FastAPI
- OpenAI GPT-4
- FAISS Vector DB
- PyPDF

## 📖 Usage

1. Upload a PDF document
2. Wait for processing
3. Ask questions about the document
4. Get instant AI-powered answers!

## 🔐 Environment Variables

Create a `.env` file in the `backend` directory:
```
OPENAI_API_KEY=your_api_key_here
```

## 📝 License

MIT License - feel free to use this project!
