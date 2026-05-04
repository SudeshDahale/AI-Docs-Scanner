import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { FileText, Trash2, Pencil, Check, X, CheckCircle2 } from 'lucide-react'

function DocumentList({ docs, onDelete, onRename }) {
  const [editingId, setEditingId] = useState(null)
  const [editValue, setEditValue] = useState('')
  const [deletingId, setDeletingId] = useState(null)

  const startEdit = (doc) => {
    setEditingId(doc.docId)
    setEditValue(doc.fileName)
  }

  const cancelEdit = () => {
    setEditingId(null)
    setEditValue('')
  }

  const confirmEdit = async (docId) => {
    if (!editValue.trim()) return
    await onRename(docId, editValue.trim())
    setEditingId(null)
    setEditValue('')
  }

  const confirmDelete = async (docId) => {
    setDeletingId(docId)
    await onDelete(docId)
    setDeletingId(null)
  }

  if (docs.length === 0) return null

  return (
    <div style={{ marginBottom: '1rem' }}>
      <AnimatePresence>
        {docs.map((doc) => (
          <motion.div
            key={doc.docId}
            initial={{ opacity: 0, y: -8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, x: -20 }}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem',
              padding: '0.5rem 0.75rem',
              background: 'rgba(255,255,255,0.05)',
              borderRadius: '10px',
              marginBottom: '0.5rem',
              border: '1px solid rgba(255,255,255,0.08)',
            }}
          >
            <CheckCircle2 size={16} color="#68d391" style={{ flexShrink: 0 }} />

            {editingId === doc.docId ? (
              <>
                <input
                  autoFocus
                  value={editValue}
                  onChange={(e) => setEditValue(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter') confirmEdit(doc.docId)
                    if (e.key === 'Escape') cancelEdit()
                  }}
                  style={{
                    flex: 1,
                    background: 'rgba(255,255,255,0.1)',
                    border: '1px solid rgba(102,126,234,0.6)',
                    borderRadius: '6px',
                    color: 'white',
                    padding: '0.2rem 0.5rem',
                    fontSize: '0.9rem',
                    outline: 'none',
                  }}
                />
                <button
                  onClick={() => confirmEdit(doc.docId)}
                  title="Save"
                  style={iconBtnStyle('#68d391')}
                >
                  <Check size={15} />
                </button>
                <button
                  onClick={cancelEdit}
                  title="Cancel"
                  style={iconBtnStyle('#fc8181')}
                >
                  <X size={15} />
                </button>
              </>
            ) : (
              <>
                <FileText size={15} color="#a0aec0" style={{ flexShrink: 0 }} />
                <span style={{
                  flex: 1,
                  color: '#e2e8f0',
                  fontSize: '0.9rem',
                  overflow: 'hidden',
                  textOverflow: 'ellipsis',
                  whiteSpace: 'nowrap',
                }}>
                  {doc.fileName}
                </span>
                <button
                  onClick={() => startEdit(doc)}
                  title="Rename"
                  style={iconBtnStyle('#90cdf4')}
                >
                  <Pencil size={14} />
                </button>
                <button
                  onClick={() => confirmDelete(doc.docId)}
                  title="Delete"
                  disabled={deletingId === doc.docId}
                  style={iconBtnStyle('#fc8181')}
                >
                  <Trash2 size={14} />
                </button>
              </>
            )}
          </motion.div>
        ))}
      </AnimatePresence>
    </div>
  )
}

const iconBtnStyle = (color) => ({
  background: 'none',
  border: 'none',
  cursor: 'pointer',
  color,
  padding: '0.2rem',
  display: 'flex',
  alignItems: 'center',
  borderRadius: '4px',
  transition: 'opacity 0.15s',
  flexShrink: 0,
})

export default DocumentList