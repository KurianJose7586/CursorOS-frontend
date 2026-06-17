import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { FileText, Folder, File, ChevronRight } from 'lucide-react';

function getFileIcon(item) {
  if (!item.includes('.')) return Folder;
  const codeExts = ['.txt', '.md', '.py', '.js', '.json', '.html', '.css', '.ts', '.jsx', '.tsx'];
  const ext = item.slice(item.lastIndexOf('.')).toLowerCase();
  if (codeExts.includes(ext)) return FileText;
  return File;
}

function getFileColor(item) {
  const ext = item.slice(item.lastIndexOf('.')).toLowerCase();
  const colors = {
    '.py': '#0A84FF',
    '.js': '#FFD60A',
    '.ts': '#3B82F6',
    '.json': '#30D158',
    '.md': '#FF453A',
    '.txt': '#9CA3AF',
    '.html': '#FF6B35',
    '.css': '#06B6D4',
    '.jsx': '#0A84FF',
    '.tsx': '#3B82F6',
  };
  return colors[ext] || '#9CA3AF';
}

function getFileName(item) {
  const parts = item.split(/[/\\]/);
  return parts[parts.length - 1] || item;
}

export default function ResultsList({ items, onSelect }) {
  const [hoveredIndex, setHoveredIndex] = useState(-1);

  if (!items || items.length === 0) return null;

  return (
    <div style={{ padding: '8px 0' }}>
      <AnimatePresence>
        {items.slice(0, 5).map((item, index) => {
          const Icon = getFileIcon(item);
          const color = getFileColor(item);
          const filename = getFileName(item);
          const isHovered = hoveredIndex === index;

          return (
            <motion.button
              key={item}
              initial={{ opacity: 0, y: 6 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{
                delay: index * 0.05,
                duration: 0.3,
                ease: [0.25, 0.1, 0.25, 1.0],
              }}
              whileHover={{ backgroundColor: 'var(--bg-card-hover)' }}
              whileTap={{ scale: 0.99 }}
              onClick={() => onSelect(item)}
              onMouseEnter={() => setHoveredIndex(index)}
              onMouseLeave={() => setHoveredIndex(-1)}
              style={{
                width: '100%',
                textAlign: 'left',
                padding: '8px 10px',
                borderRadius: 10,
                cursor: 'pointer',
                background: isHovered ? 'var(--bg-card-hover)' : 'transparent',
                border: 'none',
                display: 'flex',
                alignItems: 'center',
                gap: 12,
                transition: 'background-color 0.15s ease',
              }}
            >
              {/* Icon */}
              <div style={{
                width: 36,
                height: 36,
                borderRadius: 8,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                flexShrink: 0,
                background: `${color}18`,
                color: color,
              }}>
                <Icon size={18} />
              </div>

              {/* Text */}
              <div style={{ flex: 1, minWidth: 0 }}>
                <div style={{
                  fontSize: 13,
                  fontWeight: 600,
                  color: 'var(--text-1)',
                  overflow: 'hidden',
                  textOverflow: 'ellipsis',
                  whiteSpace: 'nowrap',
                }}>
                  {filename}
                </div>
                <div style={{
                  fontSize: 11,
                  color: 'var(--text-3)',
                  overflow: 'hidden',
                  textOverflow: 'ellipsis',
                  whiteSpace: 'nowrap',
                  marginTop: 2,
                }}>
                  {item}
                </div>
              </div>

              {/* Chevron */}
              <ChevronRight
                size={14}
                style={{
                  opacity: isHovered ? 0.25 : 0,
                  flexShrink: 0,
                  transition: 'opacity 0.15s ease',
                }}
              />
            </motion.button>
          );
        })}
      </AnimatePresence>
    </div>
  );
}
