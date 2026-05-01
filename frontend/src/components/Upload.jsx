import { useState, useRef } from 'react'
import { motion } from 'framer-motion'
import { Upload as UploadIcon, FileText, Loader2, CheckCircle2 } from 'lucide-react'
import './Upload.css'

function Upload({ onUploadSuccess }) {
  const [isDragging, setIsDragging] = useState(false)
  const [uploading, setUploading] = useState(false)
  const [uploadStatus, setUploadStatus] = useState('')
  const fileInputRef = useRef(null)

  const handleDragOver = (e) => {
    e.preventDefault()
    setIsDragging(true)
  }

  const handleDragLeave = (e) => {
    e.preventDefault()
    setIsDragging(false)
  }

  const handleDrop = async (e) => {
    e.preventDefault()
    setIsDragging(false)
    
    const files = e.dataTransfer.files
    if (files.length > 0 && files[0].type === 'application/pdf') {
      await uploadFile(files[0])
    } else {
      alert('Please upload a PDF file')
    }
  }

  const handleFileSelect = async (e) => {
    const files = e.target.files
    if (files.length > 0) {
      await uploadFile(files[0])
    }
  }

  const uploadFile = async (file) => {
    setUploading(true)
    setUploadStatus('Uploading...')

    const formData = new FormData()
    formData.append('file', file)

    try {
      const response = await fetch('http://localhost:8000/upload', {
        method: 'POST',
        body: formData
      })

      if (!response.ok) throw new Error('Upload failed')

      const data = await response.json()
      setUploadStatus('Processing complete!')
      
      setTimeout(() => {
        onUploadSuccess(data.doc_id, file.name)
      }, 1000)
    } catch (error) {
      console.error('Upload error:', error)
      setUploadStatus('Upload failed. Please try again.')
      setUploading(false)
    }
  }

  return (
    <div className="upload-container">
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
          accept=".pdf"
          onChange={handleFileSelect}
          style={{ display: 'none' }}
          disabled={uploading}
        />

        {uploading ? (
          <div className="upload-state">
            {uploadStatus === 'Processing complete!' ? (
              <>
                <CheckCircle2 size={64} className="status-icon success" />
                <p className="upload-status">{uploadStatus}</p>
              </>
            ) : (
              <>
                <Loader2 size={64} className="status-icon spinning" />
                <p className="upload-status">{uploadStatus}</p>
              </>
            )}
          </div>
        ) : (
          <div className="upload-state">
            <div className="upload-icon-wrapper">
              <FileText size={48} className="file-icon" />
              <UploadIcon size={24} className="upload-icon" />
            </div>
            <h3 className="upload-title">Drop your PDF here</h3>
            <p className="upload-subtitle">or click to browse</p>
            <div className="upload-hint">Maximum file size: 50MB</div>
          </div>
        )}
      </motion.div>
    </div>
  )
}

export default Upload
