import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import Hero from './components/Hero'
import Upload from './components/Upload'
import Chat from './components/Chat'
import Background from './components/Background'
import './App.css'

function App() {
  const [docId, setDocId] = useState(null)
  const [fileName, setFileName] = useState('')

  const handleUploadSuccess = (id, name) => {
    setDocId(id)
    setFileName(name)
  }

  const handleReset = () => {
    setDocId(null)
    setFileName('')
  }

  return (
    <div className="app">
      <Background />
      
      <AnimatePresence mode="wait">
        {!docId ? (
          <motion.div
            key="upload-view"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.5 }}
          >
            <Hero />
            <Upload onUploadSuccess={handleUploadSuccess} />
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
              docId={docId} 
              fileName={fileName}
              onReset={handleReset}
            />
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}

export default App
