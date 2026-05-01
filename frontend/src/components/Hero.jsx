import { motion } from 'framer-motion'
import { Sparkles, Zap, Brain } from 'lucide-react'
import './Hero.css'

function Hero() {
  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1,
        delayChildren: 0.2
      }
    }
  }

  const itemVariants = {
    hidden: { y: 20, opacity: 0 },
    visible: {
      y: 0,
      opacity: 1,
      transition: {
        type: "spring",
        stiffness: 100
      }
    }
  }

  return (
    <motion.div 
      className="hero"
      variants={containerVariants}
      initial="hidden"
      animate="visible"
    >
      <motion.div className="hero-badge" variants={itemVariants}>
        <Sparkles size={16} />
        <span>AI-Powered Intelligence</span>
      </motion.div>

      <motion.h1 className="hero-title" variants={itemVariants}>
        <span className="gradient-text">DocuMind</span>
      </motion.h1>

      <motion.p className="hero-subtitle" variants={itemVariants}>
        Transform your PDFs into intelligent conversations
      </motion.p>

      <motion.div className="hero-features" variants={itemVariants}>
        <div className="feature">
          <div className="feature-icon">
            <Zap size={20} />
          </div>
          <span>Instant Answers</span>
        </div>
        <div className="feature">
          <div className="feature-icon">
            <Brain size={20} />
          </div>
          <span>Deep Understanding</span>
        </div>
        <div className="feature">
          <div className="feature-icon">
            <Sparkles size={20} />
          </div>
          <span>RAG Technology</span>
        </div>
      </motion.div>
    </motion.div>
  )
}

export default Hero
