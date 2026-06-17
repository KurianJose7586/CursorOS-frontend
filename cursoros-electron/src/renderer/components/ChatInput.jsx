import { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Search, ArrowUp } from 'lucide-react';

export default function ChatInput({ onSubmit }) {
  const [value, setValue] = useState('');
  const [focused, setFocused] = useState(false);
  const inputRef = useRef(null);

  useEffect(() => {
    const timer = setTimeout(() => inputRef.current?.focus(), 100);
    return () => clearTimeout(timer);
  }, []);

  const handleSubmit = () => {
    if (value.trim()) {
      onSubmit(value.trim());
      setValue('');
    }
  };

  return (
    <div style={{ position: 'relative', flex: 1 }}>
      {/* Focus glow ring */}
      <motion.div
        animate={{
          boxShadow: focused
            ? '0 0 0 3px rgba(10, 132, 255, 0.15)'
            : '0 0 0 0px transparent',
        }}
        transition={{ duration: 0.2 }}
        style={{
          position: 'absolute',
          inset: -1,
          borderRadius: 10,
          pointerEvents: 'none',
        }}
      />

      <div style={{
        display: 'flex',
        alignItems: 'center',
        gap: 8,
        borderRadius: 10,
        padding: '8px 12px',
        background: 'var(--bg-input)',
        border: focused
          ? '1px solid rgba(10, 132, 255, 0.3)'
          : '1px solid rgba(255, 255, 255, 0.06)',
        boxShadow: focused
          ? 'inset 0 1px 0 0 rgba(255,255,255,0.08), 0 1px 3px rgba(0,0,0,0.15)'
          : 'inset 0 1px 0 0 rgba(255,255,255,0.04), 0 1px 2px rgba(0,0,0,0.10)',
        transition: 'all 0.2s ease',
      }}>
        <Search size={15} style={{ opacity: 0.3, flexShrink: 0 }} />

        <input
          ref={inputRef}
          type="text"
          value={value}
          onChange={(e) => setValue(e.target.value)}
          onFocus={() => setFocused(true)}
          onBlur={() => setFocused(false)}
          onKeyDown={(e) => {
            if (e.key === 'Enter') handleSubmit();
            if (e.key === 'Escape') window.cursoros.hideWindow();
          }}
          placeholder="Ask anything..."
          style={{
            flex: 1,
            background: 'transparent',
            border: 'none',
            outline: 'none',
            fontSize: 14,
            fontWeight: 500,
            color: 'var(--text-1)',
            caretColor: 'var(--blue)',
            minWidth: 0,
          }}
        />

        <AnimatePresence>
          {value.trim() && (
            <motion.button
              initial={{ scale: 0, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0, opacity: 0 }}
              transition={{ type: 'spring', stiffness: 600, damping: 25 }}
              onClick={handleSubmit}
              style={{
                width: 28,
                height: 28,
                borderRadius: '50%',
                background: 'var(--blue)',
                border: 'none',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                cursor: 'pointer',
                flexShrink: 0,
              }}
            >
              <ArrowUp size={14} color="white" strokeWidth={2.5} />
            </motion.button>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}
