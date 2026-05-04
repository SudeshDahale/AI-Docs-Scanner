import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import Hero from './components/Hero'
import Upload from './components/Upload'
import Chat from './components/Chat'
import Background from './components/Background'
import './App.css'

function App() {
  const [docs, setDocs] = useState([])
  const [chatStarted, setChatStarted] = useState(false)

  const handleUploadSuccess = (id, name) => {
    setDocs(prev => [...prev, { docId: id, fileName: name }])
  }

  const handleStartChat = () => {
    if (docs.length > 0) setChatStarted(true)
  }

  const handleReset = () => {
    setDocs([])
    setChatStarted(false)
  }

  // Delete a doc from state and call backend
  const handleDelete = async (docId) => {
    await fetch(`http://localhost:8000/documents/${docId}`, { method: 'DELETE' })
    setDocs(prev => prev.filter(d => d.docId !== docId))
  }

  // Rename a doc in state and call backend
  const handleRename = async (docId, newName) => {
    const formData = new FormData()
    formData.append('fileName', newName)
    await fetch(`http://localhost:8000/documents/${docId}/rename`, {
      method: 'PATCH',
      body: formData,
    })
    setDocs(prev => prev.map(d => d.docId === docId ? { ...d, fileName: newName } : d))
  }

  return (
    <div className="app">
      <Background />

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