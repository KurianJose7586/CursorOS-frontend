import { motion } from 'framer-motion';

export default function PillView() {
  return (
    <motion.div
      key="pill"
      initial={{ opacity: 0, scaleX: 0.5 }}
      animate={{ opacity: 1, scaleX: 1 }}
      exit={{ opacity: 0, scaleX: 0.5 }}
      transition={{ duration: 0.3, ease: [0.25, 0.1, 0.25, 1.0] }}
      style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        width: '100%',
        height: '100%',
        background: 'transparent',
      }}
    >
      <motion.div
        style={{
          width: 100,
          height: 4,
          borderRadius: 9999,
          background: 'linear-gradient(90deg, rgba(10,132,255,0.4), rgba(10,132,255,0.8), rgba(10,132,255,0.4))',
          boxShadow: '0 0 12px rgba(10, 132, 255, 0.3)',
          cursor: 'pointer',
        }}
        whileHover={{
          width: 120,
          boxShadow: '0 0 20px rgba(10, 132, 255, 0.5)',
        }}
        transition={{ duration: 0.2 }}
      />
    </motion.div>
  );
}
