import { motion } from 'framer-motion';
import { Play } from 'lucide-react';

export default function ActionBar({ onExecute }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: 12 }}
      transition={{ duration: 0.35, ease: [0.25, 0.1, 0.25, 1.0] }}
      style={{
        padding: '12px 20px',
        flexShrink: 0,
        display: 'flex',
        justifyContent: 'flex-end',
        borderTop: '1px solid var(--separator)',
      }}
    >
      <motion.button
        whileHover={{ scale: 1.03 }}
        whileTap={{ scale: 0.97 }}
        onClick={onExecute}
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: 8,
          padding: '9px 20px',
          borderRadius: 8,
          background: 'linear-gradient(180deg, #0A84FF 0%, #006EE6 100%)',
          color: 'white',
          border: 'none',
          fontSize: 13,
          fontWeight: 600,
          cursor: 'pointer',
          boxShadow: '0 2px 8px rgba(10, 132, 255, 0.3), inset 0 1px 0 0 rgba(255,255,255,0.15)',
        }}
      >
        <Play size={13} fill="white" />
        Execute Plan
      </motion.button>
    </motion.div>
  );
}
