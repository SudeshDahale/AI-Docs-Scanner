import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import Hero from './components/Hero'
import Upload from './components/Upload'
import Chat from './components/Chat'
import Background from './components/Background'
import AuthPage from './components/AuthPage'
import { isLoggedIn, removeToken, apiFetch } from './utils/auth'
import './App.css'

const BASE = 'http://localhost:8000'

function App() {
  const [authed, setAuthed] = useState(isLoggedIn())
  const [docs, setDocs] = useState([])
  const [chatStarted, setChatStarted] = useState(false)

  const handleAuth = () => setAuthed(true)

  const handleLogout = () => {
    removeToken()
    setAuthed(false)
    setDocs([])
    setChatStarted(false)
  }

  const handleUploadSuccess = (id, name) => {
    setDocs(prev => [...prev, { docId: id, fileName: name, status: 'processing' }])
  }

  const handleDocReady = (docId) => {
    setDocs(prev => prev.map(d => d.docId === docId ? { ...d, status: 'ready' } : d))
  }

  const handleStartChat = () => {
    if (docs.length > 0) setChatStarted(true)
  }

  const handleReset = () => {
    setDocs([])
    setChatStarted(false)
  }

  const handleDelete = async (docId) => {
    await apiFetch(`${BASE}/documents/${docId}`, { method: 'DELETE' })
    setDocs(prev => prev.filter(d => d.docId !== docId))
  }

  const handleRename = async (docId, newName) => {
    const formData = new FormData()
    formData.append('fileName', newName)
    await apiFetch(`${BASE}/documents/${docId}/rename`, { method: 'PATCH', body: formData })
    setDocs(prev => prev.map(d => d.docId === docId ? { ...d, fileName: newName } : d))
  }

  if (!authed) {
    return (
      <div className="app">
        <Background />
        <AuthPage onAuth={handleAuth} />
      </div>
    )
  }

  return (
    <div className="app">
      <Background />

      {/* Logout button */}
      <button
        onClick={handleLogout}
        style={{
          position: 'fixed', top: '1rem', right: '1rem', zIndex: 100,
          background: 'rgba(255,255,255,0.08)',
          border: '1px solid rgba(255,255,255,0.15)',
          color: 'rgba(255,255,255,0.7)', padding: '0.4rem 0.9rem',
          borderRadius: '8px', cursor: 'pointer', fontSize: '0.85rem',
        }}
      >
        Logout
      </button>

      <AnimatePresence mode="wait">
        {!chatStarted ? (
          <motion.div
            key="upload-view"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.5 }}
          >
            <Hero />
            <Upload
              onUploadSuccess={handleUploadSuccess}
              onDocReady={handleDocReady}
              uploadedDocs={docs}
              onStartChat={handleStartChat}
              onDelete={handleDelete}
              onRename={handleRename}
            />
          </motion.div>
        ) : (
          <motion.div
            key="chat-view"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.5 }}
          >
            <Chat
              docIds={docs.map(d => d.docId).join(',')}
              fileNames={docs.map(d => d.fileName)}
              onReset={handleReset}
            />
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}

export default App