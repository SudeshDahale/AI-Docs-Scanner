import { useState } from 'react'
import { motion } from 'framer-motion'
import { Sparkles, Mail, Lock, Loader2 } from 'lucide-react'
import { saveToken } from '../utils/auth'

const BASE = 'http://localhost:8000'

function AuthPage({ onAuth }) {
  const [mode, setMode] = useState('login')      // 'login' | 'register'
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setSuccess('')
    setLoading(true)

    try {
      if (mode === 'register') {
        const res = await fetch(`${BASE}/auth/register`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email, password }),
        })
        const data = await res.json()
        if (!res.ok) throw new Error(data.detail || 'Registration failed')
        setSuccess('Account created! Logging you in...')
        // auto-login after register
        await login(email, password)
      } else {
        await login(email, password)
      }
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const login = async (em, pw) => {
    const form = new URLSearchParams()
    form.append('username', em)
    form.append('password', pw)

    const res = await fetch(`${BASE}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: form.toString(),
    })
    const data = await res.json()
    if (!res.ok) throw new Error(data.detail || 'Login failed')
    saveToken(data.access_token)
    onAuth()
  }

  return (
    <div style={{
      minHeight: '100vh', display: 'flex', alignItems: 'center',
      justifyContent: 'center', padding: '1rem',
    }}>
      <motion.div
        initial={{ opacity: 0, y: 24 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
        style={{
          width: '100%', maxWidth: '420px',
          background: 'rgba(255,255,255,0.05)',
          backdropFilter: 'blur(20px)',
          border: '1px solid rgba(255,255,255,0.12)',
          borderRadius: '20px', padding: '2.5rem',
        }}
      >
        {/* Logo */}
        <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
          <div style={{
            display: 'inline-flex', alignItems: 'center', justifyContent: 'center',
            width: 56, height: 56, borderRadius: '16px',
            background: 'linear-gradient(135deg, #667eea, #764ba2)',
            marginBottom: '1rem',
          }}>
            <Sparkles size={28} color="white" />
          </div>
          <h1 style={{ color: 'white', fontSize: '1.5rem', fontWeight: 700, margin: 0 }}>
            DocuMind AI
          </h1>
          <p style={{ color: 'rgba(255,255,255,0.5)', marginTop: '0.25rem', fontSize: '0.9rem' }}>
            {mode === 'login' ? 'Sign in to your workspace' : 'Create your account'}
          </p>
        </div>

        {/* Tab switcher */}
        <div style={{
          display: 'flex', background: 'rgba(255,255,255,0.07)',
          borderRadius: '10px', padding: '4px', marginBottom: '1.5rem',
        }}>
          {['login', 'register'].map(m => (
            <button
              key={m}
              onClick={() => { setMode(m); setError(''); setSuccess('') }}
              style={{
                flex: 1, padding: '0.6rem',
                background: mode === m ? 'rgba(255,255,255,0.12)' : 'transparent',
                color: mode === m ? 'white' : 'rgba(255,255,255,0.5)',
                border: 'none', borderRadius: '8px',
                fontWeight: mode === m ? 600 : 400,
                cursor: 'pointer', fontSize: '0.9rem',
                transition: 'all 0.2s',
              }}
            >
              {m === 'login' ? 'Sign In' : 'Register'}
            </button>
          ))}
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <div style={{ position: 'relative' }}>
            <Mail size={16} style={{
              position: 'absolute', left: 14, top: '50%',
              transform: 'translateY(-50%)', color: 'rgba(255,255,255,0.4)',
            }} />
            <input
              type="email"
              placeholder="Email address"
              value={email}
              onChange={e => setEmail(e.target.value)}
              required
              style={inputStyle}
            />
          </div>

          <div style={{ position: 'relative' }}>
            <Lock size={16} style={{
              position: 'absolute', left: 14, top: '50%',
              transform: 'translateY(-50%)', color: 'rgba(255,255,255,0.4)',
            }} />
            <input
              type="password"
              placeholder="Password"
              value={password}
              onChange={e => setPassword(e.target.value)}
              required
              style={inputStyle}
            />
          </div>

          {error && (
            <motion.p
              initial={{ opacity: 0 }} animate={{ opacity: 1 }}
              style={{ color: '#ff6b6b', fontSize: '0.85rem', margin: 0, textAlign: 'center' }}
            >
              {error}
            </motion.p>
          )}

          {success && (
            <motion.p
              initial={{ opacity: 0 }} animate={{ opacity: 1 }}
              style={{ color: '#6bffb8', fontSize: '0.85rem', margin: 0, textAlign: 'center' }}
            >
              {success}
            </motion.p>
          )}

          <button
            type="submit"
            disabled={loading}
            style={{
              padding: '0.85rem',
              background: 'linear-gradient(135deg, #667eea, #764ba2)',
              color: 'white', border: 'none', borderRadius: '12px',
              fontWeight: 600, fontSize: '1rem', cursor: loading ? 'not-allowed' : 'pointer',
              opacity: loading ? 0.7 : 1,
              display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.5rem',
              transition: 'opacity 0.2s',
            }}
          >
            {loading
              ? <><Loader2 size={18} style={{ animation: 'spin 1s linear infinite' }} /> Processing...</>
              : mode === 'login' ? 'Sign In' : 'Create Account'
            }
          </button>
        </form>
      </motion.div>
    </div>
  )
}

const inputStyle = {
  width: '100%', padding: '0.75rem 0.75rem 0.75rem 2.5rem',
  background: 'rgba(255,255,255,0.07)',
  border: '1px solid rgba(255,255,255,0.12)',
  borderRadius: '10px', color: 'white', fontSize: '0.95rem',
  outline: 'none', boxSizing: 'border-box',
}

export default AuthPage