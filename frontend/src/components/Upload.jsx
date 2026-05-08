import { useState, useRef, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Upload as UploadIcon, FileText, Loader2, MessageSquare, CheckCircle, AlertCircle } from 'lucide-react'
import DocumentList from './DocumentList'
import { apiFetch } from '../utils/auth'
import './Upload.css'

const BASE = 'http://localhost:8000'

function Upload({ onUploadSuccess, onDocReady, uploadedDocs, onStartChat, onDelete, onRename }) {
  const [isDragging, setIsDragging] = useState(false)
  const [uploading, setUploading] = useState(false)
  const [uploadStatus, setUploadStatus] = useState('')
  const fileInputRef = useRef(null)

  // Poll status for any doc still processing
  useEffect(() => {
    const processing = uploadedDocs.filter(d => d.status === 'processing')
    if (processing.length === 0) return

    const interval = setInterval(async () => {
      for (const doc of processing) {
        try {
          const res = await apiFetch(`${BASE}/documents/${doc.docId}/status`)
          if (res.ok) {
            const data = await res.json()
            if (data.status === 'ready' || data.status === 'failed') {
              onDocReady(doc.docId, data.status)
            }
          }
        } catch (_) {}
      }
    }, 2000)

    return () => clearInterval(interval)
  }, [uploadedDocs, onDocReady])

  const allReady = uploadedDocs.length > 0 && uploadedDocs.every(d => d.status === 'ready')

  const handleDragOver = (e) => { e.preventDefault(); setIsDragging(true) }
  const handleDragLeave = (e) => { e.preventDefault(); setIsDragging(false) }

  const handleDrop = async (e) => {
    e.preventDefault()
    setIsDragging(false)
    const files = Array.from(e.dataTransfer.files)
    for (const file of files) await uploadFile(file)
  }

  const handleFileSelect = async (e) => {
    const files = Array.from(e.target.files)
    for (const file of files) await uploadFile(file)
  }

  const uploadFile = async (file) => {
    setUploading(true)
    setUploadStatus(`Uploading ${file.name}...`)

    const formData = new FormData()
    formData.append('file', file)

    try {
      const response = await apiFetch(`${BASE}/upload`, { method: 'POST', body: formData })
      if (!response.ok) throw new Error('Upload failed')
      const data = await response.json()
      onUploadSuccess(data.doc_id, file.name)
      setUploadStatus('')
    } catch (error) {
      console.error('Upload error:', error)
      setUploadStatus('Upload failed. Please try again.')
    } finally {
      setUploading(false)
      if (fileInputRef.current) fileInputRef.current.value = ''
    }
  }

  return (
    <div className="upload-container">
      <DocumentList docs={uploadedDocs} onDelete={onDelete} onRename={onRename} />

      <motion.div
        className={`upload-zone ${isDragging ? 'dragging' : ''} ${uploading ? 'uploading' : ''}`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => !uploading && fileInputRef.current?.click()}
        whileHover={{ scale: uploading ? 1 : 1.02 }}
        whileTap={{ scale: uploading ? 1 : 0.98 }}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf,.docx,.doc,.pptx,.ppt,.txt,.md"
          multiple
          onChange={handleFileSelect}
          style={{ display: 'none' }}
          disabled={uploading}
        />

        {uploading ? (
          <div className="upload-state">
            <Loader2 size={64} className="status-icon spinning" />
            <p className="upload-status">{uploadStatus}</p>
          </div>
        ) : (
          <div className="upload-state">
            <div className="upload-icon-wrapper">
              <FileText size={48} className="file-icon" />
              <UploadIcon size={24} className="upload-icon" />
            </div>
            <h3 className="upload-title">
              {uploadedDocs.length === 0 ? 'Drop your files here' : 'Add more files'}
            </h3>
            <p className="upload-subtitle">or click to browse — multiple files supported</p>
            <div className="upload-hint">PDF, DOCX, PPTX, TXT, MD — Max 50MB</div>
          </div>
        )}
      </motion.div>

      {/* Processing status indicators */}
      {uploadedDocs.some(d => d.status === 'processing') && (
        <motion.div
          initial={{ opacity: 0 }} animate={{ opacity: 1 }}
          style={{
            marginTop: '0.75rem', padding: '0.75rem 1rem',
            background: 'rgba(102,126,234,0.15)',
            border: '1px solid rgba(102,126,234,0.3)',
            borderRadius: '10px', display: 'flex', alignItems: 'center', gap: '0.5rem',
            color: 'rgba(255,255,255,0.8)', fontSize: '0.9rem',
          }}
        >
          <Loader2 size={16} style={{ animation: 'spin 1s linear infinite', flexShrink: 0 }} />
          Indexing documents in background… this takes a few seconds
        </motion.div>
      )}

      {uploadedDocs.some(d => d.status === 'failed') && (
        <motion.div
          initial={{ opacity: 0 }} animate={{ opacity: 1 }}
          style={{
            marginTop: '0.75rem', padding: '0.75rem 1rem',
            background: 'rgba(255,107,107,0.15)',
            border: '1px solid rgba(255,107,107,0.3)',
            borderRadius: '10px', display: 'flex', alignItems: 'center', gap: '0.5rem',
            color: '#ff6b6b', fontSize: '0.9rem',
          }}
        >
          <AlertCircle size={16} style={{ flexShrink: 0 }} />
          Some documents failed to index. Try re-uploading them.
        </motion.div>
      )}

      {allReady && (
        <motion.button
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          onClick={onStartChat}
          style={{
            marginTop: '1rem', width: '100%', padding: '0.85rem',
            background: 'linear-gradient(135deg, #667eea, #764ba2)',
            color: 'white', border: 'none', borderRadius: '12px',
            fontSize: '1rem', fontWeight: '600', cursor: 'pointer',
            display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.5rem',
          }}
        >
          <MessageSquare size={20} />
          Start Chat with {uploadedDocs.length} file{uploadedDocs.length > 1 ? 's' : ''}
        </motion.button>
      )}
    </div>
  )
}

export default Upload