import { useState, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Send, FileText, RotateCcw, Sparkles, User } from 'lucide-react'
import './Chat.css'

function Chat({ docId, fileName, onReset }) {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const messagesEndRef = useRef(null)
  const inputRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  useEffect(() => {
    inputRef.current?.focus()
  }, [])

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!input.trim() || loading) return

    const userMessage = { role: 'user', content: input }
    setMessages(prev => [...prev, userMessage])
    setInput('')
    setLoading(true)

    try {
      const formData = new FormData()
      formData.append('doc_id', docId)
      formData.append('question', input)

      const response = await fetch('http://localhost:8000/ask', {
        method: 'POST',
        body: formData
      })

      if (!response.ok) throw new Error('Failed to get answer')

      const reader = response.body.getReader()
      const decoder = new TextDecoder()
      let assistantMessage = { role: 'assistant', content: '' }
      
      setMessages(prev => [...prev, assistantMessage])

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        const chunk = decoder.decode(value)
        assistantMessage.content += chunk

        setMessages(prev => {
          const newMessages = [...prev]
          newMessages[newMessages.length - 1] = { ...assistantMessage }
          return newMessages
        })
      }
    } catch (error) {
      console.error('Chat error:', error)
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.'
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
            <span className="doc-name">{fileName}</span>
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
              <p>I'll provide answers based on the content of your PDF</p>
            </motion.div>
          )}

          {messages.map((message, index) => (
            <motion.div
              key={index}
              className={`message ${message.role}`}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
            >
              <div className="message-avatar">
                {message.role === 'user' ? (
                  <User size={18} />
                ) : (
                  <Sparkles size={18} />
                )}
              </div>
              <div className="message-content">
                {message.content}
              </div>
            </motion.div>
          ))}
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
