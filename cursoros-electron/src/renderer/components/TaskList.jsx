import { motion, AnimatePresence } from 'framer-motion';
import { CheckCircle2, XCircle } from 'lucide-react';
import AppleSpinner from './AppleSpinner';

const statusConfig = {
  pending: { color: 'rgba(255,255,255,0.15)' },
  'in-progress': { color: 'var(--blue)' },
  completed: { color: 'var(--green)' },
  failed: { color: 'var(--red)' },
};

export default function TaskList({ tasks }) {
  if (tasks.length === 0) return null;

  return (
    <div style={{ padding: '4px 0' }}>
      <AnimatePresence>
        {tasks.map((task, index) => {
          const config = statusConfig[task.status];
          const isActive = task.status === 'in-progress';

          return (
            <motion.div
              key={task.id}
              initial={{ opacity: 0, x: -8 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{
                delay: index * 0.08,
                duration: 0.3,
                ease: [0.25, 0.1, 0.25, 1.0],
              }}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: 10,
                padding: '6px 0',
              }}
            >
              {/* Status indicator */}
              <div style={{
                width: 16,
                height: 16,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                flexShrink: 0,
              }}>
                {task.status === 'in-progress' && <AppleSpinner size={14} />}
                {task.status === 'completed' && (
                  <motion.div
                    initial={{ scale: 0 }}
                    animate={{ scale: 1 }}
                    transition={{ type: 'spring', stiffness: 600, damping: 20 }}
                  >
                    <CheckCircle2 size={14} color="var(--green)" />
                  </motion.div>
                )}
                {task.status === 'failed' && (
                  <XCircle size={14} color="var(--red)" />
                )}
                {task.status === 'pending' && (
                  <div style={{
                    width: 6,
                    height: 6,
                    borderRadius: '50%',
                    background: 'rgba(255,255,255,0.15)',
                  }} />
                )}
              </div>

              {/* Description */}
              <span style={{
                fontSize: 13,
                fontWeight: isActive ? 500 : 400,
                color: isActive ? 'var(--text-1)' : 'var(--text-2)',
                transition: 'color 0.2s ease',
              }}>
                {task.description}
              </span>
            </motion.div>
          );
        })}
      </AnimatePresence>
    </div>
  );
}
