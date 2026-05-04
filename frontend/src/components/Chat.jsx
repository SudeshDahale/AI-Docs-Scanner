import { useState, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Send, FileText, RotateCcw, Sparkles, User, BookOpen, ChevronDown, ChevronUp } from 'lucide-react'
import './Chat.css'

function CitationCard({ citations }) {
  const [open, setOpen] = useState(false)
  if (!citations || citations.length === 0) return null

  return (
    <div className="citations-wrapper">
      <button className="citations-toggle" onClick={() => setOpen(o => !o)}>
        <BookOpen size={14} />
        <span>{citations.length} source{citations.length > 1 ? 's' : ''}</span>
        {open ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
      </button>

      <AnimatePresence>
        {open && (
          <motion.div
            className="citations-list"
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.2 }}
          >
            {citations.map((c, i) => (
              <div key={i} className="citation-card">
                <div className="citation-header">
                  <FileText size={13} />
                  <span className="citation-file">{c.fileName}</span>
                  <span className="citation-page">Page {c.page}</span>
                </div>
                <p className="citation-snippet">"{c.snippet}{c.snippet.length >= 200 ? '…' : ''}"</p>
              </div>
            ))}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}

function Chat({ docIds, fileNames, onReset }) {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const messagesEndRef = useRef(null)
  const inputRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => { scrollToBottom() }, [messages])
  useEffect(() => { inputRef.current?.focus() }, [])

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!input.trim() || loading) return

    const userMessage = { role: 'user', content: input }
    setMessages(prev => [...prev, userMessage])
    setInput('')
    setLoading(true)

    try {
      const formData = new FormData()
      formData.append('doc_ids', docIds)
      formData.append('question', input)

      const response = await fetch('http://localhost:8000/ask', {
        method: 'POST',
        body: formData
      })

      if (!response.ok) throw new Error('Failed to get answer')

      const data = await response.json()

      setMessages(prev => [...prev, {
        role: 'assistant',
        content: data.answer,
        citations: data.citations || [],
      }])
    } catch (error) {
      console.error('Chat error:', error)
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.',
        citations: [],
      }])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="chat-container">
      <motion.div
        className="chat-header"
        initial={{ y: -20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
      >
        <div className="header-content">
          <div className="doc-info">
            <FileText size={20} />
            <span className="doc-name">
              {Array.isArray(fileNames) ? fileNames.join(', ') : fileNames}
            </span>
          </div>
          <button className="reset-btn" onClick={onReset}>
            <RotateCcw size={18} />
            <span>New Document</span>
          </button>
        </div>
      </motion.div>

      <div className="chat-messages">
        <AnimatePresence>
          {messages.length === 0 && (
            <motion.div
              className="empty-state"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0 }}
            >
              <Sparkles size={48} />
              <h3>Ask me anything about your document</h3>
              <p>Answers will include page citations from your PDF</p>
            </motion.div>
          )}

          {messages.map((message, index) => (
            <motion.div
              key={index}
              className={`message ${message.role}`}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.05 }}
            >
              <div className="message-avatar">
                {message.role === 'user' ? <User size={18} /> : <Sparkles size={18} />}
              </div>
              <div className="message-body">
                <div className="message-content">{message.content}</div>
                {message.role === 'assistant' && (
                  <CitationCard citations={message.citations} />
                )}
              </div>
            </motion.div>
          ))}

          {loading && (
            <motion.div
              className="message assistant"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
            >
              <div className="message-avatar">
                <Sparkles size={18} />
              </div>
              <div className="message-body">
                <div className="message-content typing-indicator">
                  <span /><span /><span />
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
        <div ref={messagesEndRef} />
      </div>

      <motion.form
        className="chat-input-container"
        onSubmit={handleSubmit}
        initial={{ y: 20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
      >
        <div className="input-wrapper">
          <input
            ref={inputRef}
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask a question about your document..."
            disabled={loading}
            className="chat-input"
          />
          <button
            type="submit"
            disabled={!input.trim() || loading}
            className="send-btn"
          >
            <Send size={20} />
          </button>
        </div>
      </motion.form>
    </div>
  )
}

export default Chat