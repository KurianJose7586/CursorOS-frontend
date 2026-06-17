import { motion } from 'framer-motion';

export default function ModeToggle({ mode, onToggle }) {
  return (
    <motion.button
      whileHover={{ scale: 1.04 }}
      whileTap={{ scale: 0.96 }}
      onClick={onToggle}
      style={{
        padding: '5px 12px',
        borderRadius: 6,
        fontSize: 11,
        fontWeight: 600,
        letterSpacing: '0.02em',
        cursor: 'pointer',
        userSelect: 'none',
        flexShrink: 0,
        color: 'rgba(255,255,255,0.55)',
        background: 'rgba(255,255,255,0.06)',
        border: '1px solid rgba(255,255,255,0.04)',
        transition: 'color 0.15s ease, background 0.15s ease',
      }}
    >
      <motion.span
        key={mode}
        initial={{ opacity: 0, y: 6 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.15 }}
      >
        {mode}
      </motion.span>
    </motion.button>
  );
}
