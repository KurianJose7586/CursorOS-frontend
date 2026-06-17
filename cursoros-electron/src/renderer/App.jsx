import { useState, useEffect, useCallback } from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import Overlay from './components/Overlay';
import PillView from './components/PillView';

export default function App() {
  const [state, setState] = useState('hidden');
  const [tasks, setTasks] = useState([]);
  const [results, setResults] = useState(null);
  const [orgPreview, setOrgPreview] = useState(null);
  const [mode, setMode] = useState('Auto');
  const [planReady, setPlanReady] = useState(false);
  const [message, setMessage] = useState(null);

  useEffect(() => {
    window.cursoros.onWindowShow(() => {
      setState('visible');
    });

    window.cursoros.onWindowHide(() => {
      setState('hiding');
      setTimeout(() => {
        setState('hidden');
        resetState();
      }, 350);
    });

    window.cursoros.onBackendEvent((data) => {
      handleBackendEvent(data);
    });
  }, []);

  const resetState = () => {
    setTasks([]);
    setResults(null);
    setOrgPreview(null);
    setPlanReady(false);
    setMessage(null);
  };

  const handleBackendEvent = (data) => {
    switch (data.type) {
      case 'task_step':
        setTasks(prev => [...prev, { id: data.id, description: data.description, status: 'pending' }]);
        break;
      case 'task_status':
        setTasks(prev => prev.map(t =>
          t.id === data.id ? { ...t, status: data.status } : t
        ));
        break;
      case 'results':
        setResults(data.items);
        window.cursoros.expandWindow();
        break;
      case 'org_preview':
        setOrgPreview(data.proposal);
        window.cursoros.expandWindow();
        break;
      case 'plan_ready':
        setPlanReady(true);
        window.cursoros.expandWindow();
        break;
      case 'message':
        setMessage(data.text);
        window.cursoros.expandWindow();
        break;
      case 'hide':
        setTimeout(() => window.cursoros.hideWindow(), 2500);
        break;
    }
  };

  const handleSubmit = useCallback(async (text) => {
    resetState();
    await window.cursoros.submitQuery(text, mode);
  }, [mode]);

  const handleFileSelect = useCallback(async (filePath) => {
    await window.cursoros.openFile(filePath);
    window.cursoros.hideWindow();
  }, []);

  const handleExecutePlan = useCallback(async () => {
    setPlanReady(false);
    await window.cursoros.executePlan();
  }, []);

  const handleConfirmOrg = useCallback(async (proposal) => {
    await window.cursoros.confirmOrg(proposal);
  }, []);

  return (
    <div style={{ width: '100%', height: '100%', background: 'transparent' }}>
      <AnimatePresence mode="wait">
        {(state === 'hidden' || state === 'hiding') && (
          <PillView key="pill" />
        )}

        {(state === 'visible') && (
          <motion.div
            key="overlay"
            initial={{ opacity: 0, scale: 0.88, y: -12, filter: 'blur(10px)' }}
            animate={{ opacity: 1, scale: 1, y: 0, filter: 'blur(0px)' }}
            exit={{ opacity: 0, scale: 0.92, y: -6, filter: 'blur(6px)' }}
            transition={{ duration: 0.45, ease: [0.25, 0.1, 0.25, 1.0] }}
            style={{ width: '100%', height: '100%' }}
          >
            <Overlay
              onSubmit={handleSubmit}
              onSelect={handleFileSelect}
              onExecute={handleExecutePlan}
              onModeToggle={() => setMode(m => m === 'Auto' ? 'Plan' : 'Auto')}
              mode={mode}
              tasks={tasks}
              results={results}
              orgPreview={orgPreview}
              planReady={planReady}
              message={message}
              onConfirmOrg={handleConfirmOrg}
            />
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
