# DocuMind - AI-Powered PDF Intelligence

A beautiful, modern web application that transforms PDFs into intelligent conversations using RAG (Retrieval Augmented Generation) technology.

## 🌟 Features

- **Drag & Drop Upload**: Easy PDF file upload with visual feedback
- **Intelligent Q&A**: Ask questions about your PDF and get accurate answers
- **Streaming Responses**: Real-time, typewriter-style AI responses
- **Beautiful UI**: Modern, gradient-based design with smooth animations
- **Responsive**: Works perfectly on desktop and mobile devices

## 📋 Prerequisites

- Node.js (v16 or higher)
- Python 3.8+
- OpenAI API Key

## 🚀 Setup Instructions

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the backend directory:
```bash
OPENAI_API_KEY=your_openai_api_key_here
```

4. Start the backend server:
```bash
uvicorn main:app --reload --port 8000
```

The backend will be running at `http://localhost:8000`

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

The frontend will be running at `http://localhost:3000`

## 🎯 Usage

1. Open your browser and go to `http://localhost:3000`
2. Upload a PDF file by dragging and dropping or clicking the upload area
3. Wait for the file to be processed
4. Start asking questions about your document!
5. The AI will provide answers based on the content of your PDF

## 🏗️ Project Structure

```
.
├── backend/
│   ├── main.py              # FastAPI application
│   ├── routes/
│   │   └── upload.py        # API endpoints
│   ├── services/
│   │   ├── pdf.py          # PDF processing
│   │   ├── rag.py          # RAG implementation
│   │   └── llm.py          # LLM integration
│   ├── storage/            # Vector store and chunks
│   └── requirements.txt    # Python dependencies
│
└── frontend/
    ├── src/
    │   ├── components/
    │   │   ├── Background.jsx    # Animated background
    │   │   ├── Hero.jsx         # Landing page hero
    │   │   ├── Upload.jsx       # File upload component
    │   │   └── Chat.jsx         # Chat interface
    │   ├── App.jsx              # Main application
    │   ├── main.jsx             # React entry point
    │   └── index.css            # Global styles
    ├── index.html
    ├── package.json
    └── vite.config.js
```

## 🎨 Design Features

- **Futuristic Aesthetic**: Gradient backgrounds, glowing effects, and smooth animations
- **Custom Fonts**: Syne for headings, JetBrains Mono for code
- **Color Scheme**: Dark theme with cyan/green accents
- **Responsive Design**: Mobile-first approach
- **Accessibility**: Keyboard navigation and screen reader support

## 🛠️ Technologies Used

### Frontend
- React 18
- Vite
- Framer Motion (animations)
- Lucide React (icons)

### Backend
- FastAPI
- OpenAI API
- FAISS (vector search)
- PyPDF (PDF processing)

## 📝 API Endpoints

- `POST /upload` - Upload and process a PDF file
- `POST /ask` - Ask a question about the uploaded document (streaming response)

## 🔒 Environment Variables

Backend `.env` file:
```
OPENAI_API_KEY=your_api_key_here
```

## 🤝 Contributing

Feel free to submit issues and enhancement requests!

## 📄 License

This project is open source and available under the MIT License.
