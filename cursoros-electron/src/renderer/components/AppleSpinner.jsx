import { motion } from 'framer-motion';

export default function AppleSpinner({ size = 14, color = 'rgba(255,255,255,0.5)' }) {
  return (
    <motion.svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      animate={{ rotate: 320 }}
      transition={{
        duration: 1,
        repeat: Infinity,
        ease: 'linear',
      }}
    >
      <circle
        cx="12"
        cy="12"
        r="9"
        fill="none"
        stroke={color}
        strokeWidth="2.5"
        strokeLinecap="round"
        strokeDasharray="40 14"
      />
    </motion.svg>
  );
}
