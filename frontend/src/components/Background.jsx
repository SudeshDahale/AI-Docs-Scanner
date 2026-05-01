import { motion } from 'framer-motion'
import './Background.css'

function Background() {
  return (
    <div className="background">
      {/* Gradient Orbs */}
      <motion.div 
        className="orb orb-1"
        animate={{
          x: [0, 100, 0],
          y: [0, -100, 0],
          scale: [1, 1.2, 1],
        }}
        transition={{
          duration: 20,
          repeat: Infinity,
          ease: "easeInOut"
        }}
      />
      <motion.div 
        className="orb orb-2"
        animate={{
          x: [0, -100, 0],
          y: [0, 100, 0],
          scale: [1, 1.1, 1],
        }}
        transition={{
          duration: 15,
          repeat: Infinity,
          ease: "easeInOut"
        }}
      />
      
      {/* Grid overlay */}
      <div className="grid-overlay" />
      
      {/* Noise texture */}
      <div className="noise" />
    </div>
  )
}

export default Background
