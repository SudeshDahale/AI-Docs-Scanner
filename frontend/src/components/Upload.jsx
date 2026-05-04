import { useState, useRef } from 'react'
import { motion } from 'framer-motion'
import { Upload as UploadIcon, FileText, Loader2, MessageSquare } from 'lucide-react'
import DocumentList from './DocumentList'
import './Upload.css'

function Upload({ onUploadSuccess, uploadedDocs, onStartChat, onDelete, onRename }) {
  const [isDragging, setIsDragging] = useState(false)
  const [uploading, setUploading] = useState(false)
  const [uploadStatus, setUploadStatus] = useState('')
  const fileInputRef = useRef(null)

  const handleDragOver = (e) => { e.preventDefault(); setIsDragging(true) }
  const handleDragLeave = (e) => { e.preventDefault(); setIsDragging(false) }

  const handleDrop = async (e) => {
    e.preventDefault()
    setIsDragging(false)
    const files = Array.from(e.dataTransfer.files).filter(f => f.type === 'application/pdf')
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
      const response = await fetch('http://localhost:8000/upload', {
        method: 'POST',
        body: formData
      })

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
      {/* Document list with delete + rename */}
      <DocumentList
        docs={uploadedDocs}
        onDelete={onDelete}
        onRename={onRename}
      />

      {/* Drop zone */}
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
              {uploadedDocs.length === 0 ? 'Drop your PDFs here' : 'Add more PDFs'}
            </h3>
            <p className="upload-subtitle">or click to browse — multiple files supported</p>
            <div className="upload-hint">Maximum file size: 50MB</div>
          </div>
        )}
      </motion.div>

      {/* Start chat button */}
      {uploadedDocs.length > 0 && !uploading && (
        <motion.button
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          onClick={onStartChat}
          style={{
            marginTop: '1rem', width: '100%', padding: '0.85rem',
            background: 'linear-gradient(135deg, #667eea, #764ba2)',
            color: 'white', border: 'none', borderRadius: '12px',
            fontSize: '1rem', fontWeight: '600', cursor: 'pointer',
            display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.5rem'
          }}
        >
          <MessageSquare size={20} />
          Start Chat with {uploadedDocs.length} PDF{uploadedDocs.length > 1 ? 's' : ''}
        </motion.button>
      )}
    </div>
  )
}

export default Upload