import ChatInput from './ChatInput';
import TaskList from './TaskList';
import ResultsList from './ResultsList';
import OrgPreview from './OrgPreview';
import ActionBar from './ActionBar';
import ModeToggle from './ModeToggle';

export default function Overlay({
  onSubmit, onSelect, onExecute, onModeToggle,
  mode, tasks, results, orgPreview, planReady, message,
  onConfirmOrg
}) {
  return (
    <div className="apple-glass" style={{
      width: '100%',
      height: '100%',
      display: 'flex',
      flexDirection: 'column',
      overflow: 'hidden',
    }}>
      {/* ── Header / Input Area ── */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        gap: 12,
        padding: '14px 20px',
        flexShrink: 0,
      }}>
        <ModeToggle mode={mode} onToggle={onModeToggle} />
        <ChatInput onSubmit={onSubmit} />
      </div>

      {/* ── Separator ── */}
      <div style={{
        height: 1,
        margin: '0 20px',
        background: 'var(--separator)',
        flexShrink: 0,
      }} />

      {/* ── Content Area ── */}
      <div className="apple-scroll" style={{
        flex: 1,
        overflowY: 'auto',
        padding: '8px 16px',
      }}>
        <TaskList tasks={tasks} />

        {results && <ResultsList items={results} onSelect={onSelect} />}

        {orgPreview && (
          <OrgPreview proposal={orgPreview} onConfirm={onConfirmOrg} />
        )}

        {message && (
          <p style={{
            fontSize: 14,
            lineHeight: 1.6,
            color: 'rgba(255,255,255,0.7)',
            padding: '12px 4px',
          }}>
            {message}
          </p>
        )}
      </div>

      {/* ── Action Bar ── */}
      {planReady && <ActionBar onExecute={onExecute} />}
    </div>
  );
}
