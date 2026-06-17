import { useState } from 'react';
import { motion } from 'framer-motion';
import { ArrowRight } from 'lucide-react';

export default function OrgPreview({ proposal, onConfirm }) {
  const [items, setItems] = useState(
    proposal.map(p => ({ file: p.file, target: p.target }))
  );

  const handleChange = (index, value) => {
    setItems(prev => prev.map((item, i) =>
      i === index ? { ...item, target: value } : item
    ));
  };

  const handleConfirm = () => {
    onConfirm(items);
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      style={{ padding: '12px 0' }}
    >
      {/* Section title */}
      <div style={{
        fontSize: 11,
        fontWeight: 600,
        letterSpacing: '0.04em',
        textTransform: 'uppercase',
        color: 'var(--text-3)',
        marginBottom: 12,
      }}>
        Organization Plan
      </div>

      {/* Items */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
        {items.map((item, index) => (
          <motion.div
            key={index}
            initial={{ opacity: 0, x: -6 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: index * 0.04, duration: 0.25 }}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: 8,
              padding: '8px 10px',
              borderRadius: 8,
              background: 'var(--bg-card)',
            }}
          >
            {/* File name */}
            <span style={{
              fontSize: 12,
              color: 'var(--text-1)',
              fontWeight: 500,
              flex: 1,
              minWidth: 0,
              overflow: 'hidden',
              textOverflow: 'ellipsis',
              whiteSpace: 'nowrap',
            }}>
              {item.file.length > 28 ? item.file.slice(0, 25) + '...' : item.file}
            </span>

            <ArrowRight size={12} style={{ opacity: 0.2, flexShrink: 0 }} />

            {/* Target input */}
            <input
              value={item.target}
              onChange={(e) => handleChange(index, e.target.value)}
              style={{
                width: 100,
                padding: '4px 8px',
                borderRadius: 6,
                border: '1px solid var(--separator)',
                background: 'var(--bg-input)',
                color: 'var(--text-1)',
                fontSize: 12,
                outline: 'none',
                textAlign: 'right',
              }}
            />
          </motion.div>
        ))}
      </div>

      {/* Confirm button */}
      <motion.button
        whileHover={{ scale: 1.02 }}
        whileTap={{ scale: 0.98 }}
        onClick={handleConfirm}
        style={{
          marginTop: 14,
          marginLeft: 'auto',
          display: 'flex',
          alignItems: 'center',
          gap: 6,
          padding: '8px 18px',
          borderRadius: 8,
          background: 'var(--green)',
          color: 'white',
          border: 'none',
          fontSize: 13,
          fontWeight: 600,
          cursor: 'pointer',
          boxShadow: '0 2px 8px rgba(48, 209, 88, 0.25)',
        }}
      >
        Execute Organization
      </motion.button>
    </motion.div>
  );
}
