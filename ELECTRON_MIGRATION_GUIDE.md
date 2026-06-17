# 🚀 CursorOS → ElectronJS Migration Guide
## *From Tkinter Overlay to Beautiful Desktop App*

> **🎨 Design Direction:** This guide follows Apple's design philosophy. See [`APPLE_DESIGN_GUIDE.md`](./APPLE_DESIGN_GUIDE.md) for the complete design system — spatial layout, color tokens, typography scale, animation physics, and sound design.

---

## 📋 Table of Contents

1. [Why ElectronJS?](#1-why-electronjs)
2. [Architecture Overview](#2-architecture-overview)
3. [Phase 1: Project Scaffolding](#3-phase-1-project-scaffolding)
4. [Phase 2: Main Process (Backend Bridge)](#4-phase-2-main-process-backend-bridge)
5. [Phase 3: Renderer Process (Beautiful UI)](#5-phase-3-renderer-process-beautiful-ui)
6. [Phase 4: Python Backend Integration](#6-phase-4-python-backend-integration)
7. [Phase 5: System Tray & Global Hotkeys](#7-phase-5-system-tray--global-hotkeys)
8. [Phase 6: Transparency & Window Management](#8-phase-6-transparency--window-management)
9. [Phase 7: Packaging & Distribution](#9-phase-7-packaging--distribution)
10. [Design System & Aesthetics](#10-design-system--aesthetics)
11. [Troubleshooting & Gotchas](#11-troubleshooting--gotchas)

---

## 1. Why ElectronJS?

### The Problem with Current Tkinter UI

Your current frontend (`frontend/overlay/window.py`) uses **Tkinter**, which has hard limits:

| Limitation | Impact on CursorOS |
|---|---|
| No CSS/styling engine | Every visual effect is manual, fragile |
| No GPU acceleration | Animations are CPU-bound, janky |
| No web tech ecosystem | Can't use React, Tailwind, Framer Motion |
| Poor font rendering | Text looks blurry on HiDPI displays |
| No SVG/icon support | Limited to bitmap images |
| No scrollable smooth lists | Result lists feel clunky |

### What ElectronJS Gives You

```
┌─────────────────────────────────────────────────────┐
│  Electron App                                        │
│  ┌───────────────────────────────────────────────┐  │
│  │  Renderer (Chromium)                          │  │
│  │  • React / Vue / Svelte                       │  │
│  │  • Tailwind CSS + custom animations           │  │
│  │  • Framer Motion for spring physics           │  │
│  │  • SVG icons, custom fonts, backdrop-filter   │  │
│  │  • GPU-composited, 60fps animations           │  │
│  └──────────────┬────────────────────────────────┘  │
│                 │  IPC (contextBridge)                │
│  ┌──────────────▼────────────────────────────────┐  │
│  │  Main Process (Node.js)                       │  │
│  │  • System tray, global hotkeys                │  │
│  │  • Spawn Python backend as child process      │  │
│  │  • File system access, OS APIs                │  │
│  │  • Window management (transparent, frameless) │  │
│  └──────────────┬────────────────────────────────┘  │
│                 │  stdio / HTTP                       │
│  ┌──────────────▼────────────────────────────────┐  │
│  │  Python Backend (existing, mostly unchanged)  │  │
│  │  • Agent, LLM calls, file operations          │  │
│  │  • Windows API (pywin32, ctypes)              │  │
│  └───────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘
```

**Key insight:** Your Python backend (`backend/`) stays almost entirely intact. Electron replaces **only** the `frontend/overlay/window.py` Tkinter code. The Python backend becomes a child process that Electron communicates with.

---

## 2. Architecture Overview

### Current Architecture (Tkinter)
```
keyboard hotkey → ActivationManager → Tkinter mainloop
                                      ↕ (function calls)
                                   Python backend (agent, llm, tasks)
```

### Target Architecture (Electron)
```
global hotkey (Electron) → Transparent overlay window
                           ↕ IPC (contextBridge)
                        Main process
                           ↕ (spawn / stdio / HTTP)
                        Python backend (agent, llm, tasks)
```

### Communication Strategy

The cleanest approach: **run your Python backend as a local HTTP server**, and have Electron call it via `fetch()`.

**Why HTTP over stdio?**
- Your Python backend already has structured data (JSON plans, file lists)
- HTTP is debuggable (you can test endpoints in a browser)
- No custom protocol to maintain
- Works even if Electron window reloads during development

```
Electron Renderer  →  Electron Main  →  Python HTTP Server (localhost:9182)
     (React UI)        (Node.js)         (FastAPI/Flask wrapper
                                          around existing backend/)
```

---

## 3. Phase 1: Project Scaffolding

### Step 1.1: Initialize the Electron Project

Create a new directory for the Electron app alongside your existing code:

```bash
# From the DONA project root
mkdir cursoros-electron
cd cursoros-electron
npm init -y
```

### Step 1.2: Install Dependencies

```bash
# Core
npm install electron --save-dev
npm install electron-builder --save-dev

# Renderer UI
npm install react react-dom
npm install @vitejs/plugin-react vite --save-dev
npm install tailwindcss @tailwindcss/vite --save-dev
npm install framer-motion lucide-react

# Dev tools
npm install electron-reload --save-dev
npm install concurrently wait-on --save-dev
```

### Step 1.3: Project Structure

```
cursoros-electron/
├── package.json
├── electron.vite.config.mjs     # Vite config for Electron
├── src/
│   ├── main/                    # Electron main process
│   │   ├── index.js             # Entry point
│   │   ├── window-manager.js    # Transparent overlay window
│   │   ├── tray-manager.js      # System tray
│   │   ├── hotkey-manager.js    # Global hotkey registration
│   │   └── python-bridge.js     # Spawn & communicate with Python
│   ├── preload/
│   │   └── index.js             # contextBridge (secure IPC)
│   └── renderer/                # React app
│       ├── index.html
│       ├── main.jsx
│       ├── App.jsx
│       ├── components/
│       │   ├── Overlay.jsx      # Main overlay container
│       │   ├── ChatInput.jsx    # Input bar with glow effects
│       │   ├── TaskList.jsx     # Animated task step list
│       │   ├── ResultsList.jsx  # File results with icons
│       │   ├── OrgPreview.jsx   # Organization plan preview
│       │   ├── ModeToggle.jsx   # Auto/Plan mode switcher
│       │   └── ActionBar.jsx    # Execute plan button
│       ├── hooks/
│       │   ├── useBackend.js    # Communicate with Python
│       │   └── useAnimation.js  # Shared animation logic
│       └── styles/
│           └── globals.css      # Tailwind + custom CSS
└── build/                       # Packaged output
```

### Step 1.4: package.json Scripts

```json
{
  "name": "cursoros",
  "version": "2.0.0",
  "main": "./src/main/index.js",
  "scripts": {
    "dev": "vite",
    "build": "vite build && electron-builder",
    "start": "concurrently \"vite\" \"wait-on http://localhost:5173 && electron .\"",
    "pack": "electron-builder --dir",
    "dist": "electron-builder"
  },
  "build": {
    "appId": "com.cursoros.app",
    "productName": "CursorOS",
    "directories": {
      "output": "dist"
    },
    "win": {
      "target": "nsis",
      "icon": "assets/icon.ico"
    },
    "files": [
      "src/main/**/*",
      "src/preload/**/*",
      "build/renderer/**/*"
    ]
  }
}
```

---

## 4. Phase 2: Main Process (Backend Bridge)

### Step 2.1: Main Entry Point (`src/main/index.js`)

```javascript
const { app, ipcMain } = require('electron');
const WindowManager = require('./window-manager');
const TrayManager = require('./tray-manager');
const HotkeyManager = require('./hotkey-manager');
const PythonBridge = require('./python-bridge');

let windowManager;
let trayManager;
let hotkeyManager;
let pythonBridge;

// Prevent multiple instances
const gotTheLock = app.requestSingleInstanceLock();
if (!gotTheLock) {
  app.quit();
}

app.whenReady().then(async () => {
  // 1. Start Python backend first
  pythonBridge = new PythonBridge();
  await pythonBridge.start();

  // 2. Create the transparent overlay window
  windowManager = new WindowManager();
  windowManager.create();

  // 3. Setup system tray
  trayManager = new TrayManager({
    onActivate: () => windowManager.toggle(),
    onQuit: () => app.quit()
  });

  // 4. Register global hotkey
  hotkeyManager = new HotkeyManager({
    onActivate: () => windowManager.toggle()
  });

  console.log('🚀 CursorOS Electron is running.');
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit();
});

app.on('before-quit', async () => {
  await pythonBridge.stop();
});
```

### Step 2.2: Transparent Overlay Window (`src/main/window-manager.js`)

This is the **most critical piece** — replacing Tkinter's `overrideredirect` + transparency:

```javascript
const { BrowserWindow, screen } = require('electron');
const path = require('path');

class WindowManager {
  constructor() {
    this.window = null;
    this.isExpanded = false;

    // Match your current Tkinter dimensions
    this.collapsedBounds = {
      width: 120,
      height: 4,
      x: 0, y: 0  // Will be centered
    };
    this.expandedBounds = {
      width: 680,
      height: 520,
      x: 0, y: 60
    };
  }

  create() {
    const { width: screenW, height: screenH } = screen.getPrimaryDisplay().workAreaSize;

    this.window = new BrowserWindow({
      width: this.collapsedBounds.width,
      height: this.collapsedBounds.height,
      x: Math.floor((screenW - this.collapsedBounds.width) / 2),
      y: this.collapsedBounds.y,

      // ── These 4 properties replace Tkinter's overrideredirect ──
      frame: false,           // No window chrome
      transparent: true,      // Enable per-pixel transparency
      hasShadow: false,       // No drop shadow
      skipTaskbar: true,      // Don't show in taskbar

      // ── Additional settings ──
      alwaysOnTop: true,      // Replace Tkinter's -topmost
      resizable: false,
      movable: false,
      focusable: true,
      show: false,            // Start hidden (like Tkinter's withdraw())

      webPreferences: {
        preload: path.join(__dirname, '..', 'preload', 'index.js'),
        contextIsolation: true,
        nodeIntegration: false,
        sandbox: false
      }
    });

    // Load the React app
    if (process.env.VITE_DEV_SERVER_URL) {
      this.window.loadURL(process.env.VITE_DEV_SERVER_URL);
    } else {
      this.window.loadFile(path.join(__dirname, '..', '..', 'build', 'renderer', 'index.html'));
    }

    // Prevent the window from being captured by screen recording
    this.window.setContentProtection(true);
  }

  toggle() {
    if (!this.window) return;

    if (this.window.isVisible()) {
      this.hide();
    } else {
      this.show();
    }
  }

  show() {
    this.isExpanded = false;
    const { width: screenW } = screen.getPrimaryDisplay().workAreaSize;

    // Start from collapsed pill dimensions
    this.window.setBounds({
      width: this.collapsedBounds.width,
      height: this.collapsedBounds.height,
      x: Math.floor((screenW - this.collapsedBounds.width) / 2),
      y: 0
    });

    this.window.show();
    this.window.focus();

    // Tell renderer to start expand animation
    this.window.webContents.send('window:show');
  }

  hide() {
    // Tell renderer to start collapse animation
    this.window.webContents.send('window:hide');

    // After animation completes, actually hide
    setTimeout(() => {
      this.window.hide();
      this.isExpanded = false;
    }, 300);
  }

  expandForContent() {
    if (this.isExpanded) return;
    this.isExpanded = true;

    const { width: screenW } = screen.getPrimaryDisplay().workAreaSize;
    this.window.setBounds({
      width: this.expandedBounds.width,
      height: this.expandedBounds.height,
      x: Math.floor((screenW - this.expandedBounds.width) / 2),
      y: this.expandedBounds.y
    });
  }
}

module.exports = WindowManager;
```

### Step 2.3: Preload Script (`src/preload/index.js`)

This is the **secure bridge** between renderer and main:

```javascript
const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('cursoros', {
  // ── Window Events ──
  onWindowShow: (callback) => ipcRenderer.on('window:show', callback),
  onWindowHide: (callback) => ipcRenderer.on('window:hide', callback),

  // ── Backend Communication ──
  submitQuery: (text, mode) => ipcRenderer.invoke('backend:submit', text, mode),
  onBackendEvent: (callback) => ipcRenderer.on('backend:event', (_, data) => callback(data)),

  // ── Window Controls ──
  expandWindow: () => ipcRenderer.send('window:expand'),
  hideWindow: () => ipcRenderer.send('window:hide'),

  // ── Actions ──
  executePlan: () => ipcRenderer.invoke('backend:execute'),
  confirmOrg: (proposal) => ipcRenderer.invoke('backend:confirm-org', proposal),
  openFile: (path) => ipcRenderer.invoke('backend:open-file', path),
});
```

### Step 2.4: Python Bridge (`src/main/python-bridge.js`)

```javascript
const { spawn } = require('child_process');
const path = require('path');
const http = require('http');

class PythonBridge {
  constructor() {
    this.process = null;
    this.port = 9182;
    this.projectRoot = path.join(__dirname, '..', '..', '..');
  }

  async start() {
    const pythonPath = path.join(
      this.projectRoot, 'backend', 'venv', 'Scripts', 'python.exe'
    );
    const wrapperPath = path.join(
      this.projectRoot, 'cursoros-electron', 'src', 'main', 'server_wrapper.py'
    );

    return new Promise((resolve, reject) => {
      this.process = spawn(pythonPath, [wrapperPath], {
        cwd: this.projectRoot,
        env: {
          ...process.env,
          CURSOROS_HTTP_PORT: this.port.toString()
        },
        stdio: ['pipe', 'pipe', 'pipe']
      });

      this.process.stdout.on('data', (data) => {
        console.log(`[Python] ${data.toString().trim()}`);
        if (data.toString().includes('SERVER_READY')) {
          resolve();
        }
      });

      this.process.stderr.on('data', (data) => {
        console.error(`[Python ERR] ${data.toString().trim()}`);
      });

      this.process.on('exit', (code) => {
        console.log(`Python process exited with code ${code}`);
      });

      // Timeout fallback
      setTimeout(() => resolve(), 5000);
    });
  }

  async stop() {
    if (this.process) {
      this.process.kill();
    }
  }

  async call(endpoint, method = 'GET', body = null) {
    return new Promise((resolve, reject) => {
      const options = {
        hostname: 'localhost',
        port: this.port,
        path: endpoint,
        method: method,
        headers: { 'Content-Type': 'application/json' }
      };

      const req = http.request(options, (res) => {
        let data = '';
        res.on('data', chunk => data += chunk);
        res.on('end', () => {
          try { resolve(JSON.parse(data)); }
          catch { resolve(data); }
        });
      });

      req.on('error', reject);
      req.setTimeout(30000, () => { req.destroy(); reject(new Error('Timeout')); });

      if (body) req.write(JSON.stringify(body));
      req.end();
    });
  }
}

module.exports = PythonBridge;
```

---

## 5. Phase 3: Renderer Process (Beautiful UI)

### Step 3.1: Global Styles (`src/renderer/styles/globals.css`)

```css
@import "tailwindcss";

/* ── Design Tokens (matching your current color scheme) ── */
:root {
  --bg-primary: #0D0D0E;
  --bg-secondary: #161618;
  --border-color: #232326;
  --accent: #3B82F6;
  --accent-glow: rgba(59, 130, 246, 0.4);
  --text-main: #F3F4F6;
  --text-dim: #9CA3AF;
  --success: #10B981;
  --error: #EF4444;
}

/* ── Base ── */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html, body, #root {
  width: 100%;
  height: 100%;
  overflow: hidden;
  background: transparent;
  font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
  color: var(--text-main);
  -webkit-font-smoothing: antialiased;
}

/* ── Glass Container ── */
.glass-panel {
  background: rgba(13, 13, 14, 0.85);
  backdrop-filter: blur(24px) saturate(1.4);
  -webkit-backdrop-filter: blur(24px) saturate(1.4);
  border: 1px solid rgba(35, 35, 38, 0.6);
  border-radius: 16px;
  box-shadow:
    0 0 0 1px rgba(59, 130, 246, 0.08),
    0 8px 32px rgba(0, 0, 0, 0.6),
    0 0 80px rgba(59, 130, 246, 0.06);
}

/* ── Glow Input ── */
.glow-input {
  background: transparent;
  border: none;
  outline: none;
  color: var(--text-main);
  font-size: 15px;
  width: 100%;
  caret-color: var(--accent);
}

.glow-input::placeholder {
  color: var(--text-dim);
  opacity: 0.6;
}

.glow-input:focus {
  text-shadow: 0 0 20px rgba(59, 130, 246, 0.3);
}

/* ── Scrollbar ── */
.custom-scrollbar::-webkit-scrollbar {
  width: 4px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background: var(--border-color);
  border-radius: 4px;
}
.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: var(--accent);
}

/* ── Animations ── */
@keyframes pulse-glow {
  0%, 100% { box-shadow: 0 0 12px rgba(59, 130, 246, 0.2); }
  50% { box-shadow: 0 0 24px rgba(59, 130, 246, 0.4); }
}

@keyframes shimmer {
  0% { background-position: -200% 0; }
  100% { background-position: 200% 0; }
}

.shimmer-loading {
  background: linear-gradient(
    90deg,
    transparent 0%,
    rgba(59, 130, 246, 0.08) 50%,
    transparent 100%
  );
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
}
```

### Step 3.2: Main App Component (`src/renderer/App.jsx`)

```jsx
import { useState, useEffect, useCallback, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import Overlay from './components/Overlay';
import PillView from './components/PillView';

export default function App() {
  const [state, setState] = useState('hidden'); // 'hidden' | 'pill' | 'expanding' | 'visible' | 'expanded'
  const [tasks, setTasks] = useState([]);
  const [results, setResults] = useState(null);
  const [orgPreview, setOrgPreview] = useState(null);
  const [mode, setMode] = useState('Auto');
  const [planReady, setPlanReady] = useState(false);
  const [message, setMessage] = useState(null);

  useEffect(() => {
    // Listen for window events from main process
    window.cursoros.onWindowShow(() => {
      setState('expanding');
      setTimeout(() => setState('visible'), 50);
    });

    window.cursoros.onWindowHide(() => {
      setState('visible');
      setTimeout(() => {
        setState('hidden');
        resetState();
      }, 300);
    });

    // Listen for backend events
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
    setState('visible');
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
    <div className="w-full h-full">
      <AnimatePresence mode="wait">
        {state === 'hidden' && (
          <PillView key="pill" onShow={() => window.cursoros.showOverlay?.()} />
        )}

        {(state === 'expanding' || state === 'visible' || state === 'expanded') && (
          <motion.div
            key="overlay"
            initial={{ opacity: 0, scale: 0.8, y: -20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: -10 }}
            transition={{ type: 'spring', stiffness: 400, damping: 30 }}
            className="w-full h-full"
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
```

### Step 3.3: Overlay Component (`src/renderer/components/Overlay.jsx`)

```jsx
import { motion } from 'framer-motion';
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
    <div className="glass-panel w-full h-full flex flex-col overflow-hidden">
      {/* ── Header / Input Area ── */}
      <div className="flex items-center gap-3 px-4 py-3 shrink-0">
        <ModeToggle mode={mode} onToggle={onModeToggle} />
        <ChatInput
          placeholder="Search or command..."
          onSubmit={onSubmit}
        />
      </div>

      {/* ── Divider ── */}
      <div className="h-px bg-[var(--border-color)] mx-4" />

      {/* ── Content Area ── */}
      <div className="flex-1 overflow-y-auto custom-scrollbar px-5 py-3">
        <TaskList tasks={tasks} />

        {results && <ResultsList items={results} onSelect={onSelect} />}

        {orgPreview && (
          <OrgPreview proposal={orgPreview} onConfirm={onConfirmOrg} />
        )}

        {message && (
          <motion.p
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-[var(--text-main)] text-sm leading-relaxed py-4"
          >
            {message}
          </motion.p>
        )}
      </div>

      {/* ── Action Bar ── */}
      {planReady && <ActionBar onExecute={onExecute} />}
    </div>
  );
}
```

### Step 3.4: Chat Input with Glow (`src/renderer/components/ChatInput.jsx`)

```jsx
import { useState, useRef, useEffect } from 'react';
import { motion } from 'framer-motion';
import { ArrowUp } from 'lucide-react';

export default function ChatInput({ placeholder, onSubmit }) {
  const [value, setValue] = useState('');
  const [focused, setFocused] = useState(false);
  const inputRef = useRef(null);

  useEffect(() => {
    // Auto-focus when component mounts
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
    <motion.div
      className="flex-1 relative"
      animate={{
        boxShadow: focused
          ? '0 0 20px rgba(59, 130, 246, 0.15), inset 0 0 12px rgba(59, 130, 246, 0.05)'
          : '0 0 0px transparent'
      }}
      transition={{ duration: 0.3 }}
    >
      {/* Glow border */}
      <motion.div
        className="absolute inset-0 rounded-xl pointer-events-none"
        animate={{
          border: focused
            ? '1px solid rgba(59, 130, 246, 0.4)'
            : '1px solid transparent'
        }}
        style={{ borderRadius: 12 }}
      />

      <div className="flex items-center gap-2 px-1">
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
          placeholder={placeholder}
          className="glow-input py-2 px-1"
        />

        <motion.button
          whileHover={{ scale: 1.1 }}
          whileTap={{ scale: 0.9 }}
          onClick={handleSubmit}
          className="p-1.5 rounded-lg transition-colors"
          style={{
            color: focused ? 'var(--accent)' : 'var(--text-dim)',
            background: focused ? 'rgba(59, 130, 246, 0.1)' : 'transparent'
          }}
        >
          <ArrowUp size={18} strokeWidth={2.5} />
        </motion.button>
      </div>
    </motion.div>
  );
}
```

### Step 3.5: Animated Task List (`src/renderer/components/TaskList.jsx`)

```jsx
import { motion, AnimatePresence } from 'framer-motion';
import { Circle, CheckCircle2, XCircle, Loader2 } from 'lucide-react';

const statusConfig = {
  pending: { icon: Circle, color: '#272729', label: 'Pending' },
  'in-progress': { icon: Loader2, color: 'var(--accent)', label: 'In Progress' },
  completed: { icon: CheckCircle2, color: 'var(--success)', label: 'Completed' },
  failed: { icon: XCircle, color: 'var(--error)', label: 'Failed' },
};

export default function TaskList({ tasks }) {
  return (
    <div className="space-y-1 py-2">
      <AnimatePresence>
        {tasks.map((task, index) => {
          const config = statusConfig[task.status];
          const Icon = config.icon;

          return (
            <motion.div
              key={task.id}
              initial={{ opacity: 0, x: -12, height: 0 }}
              animate={{ opacity: 1, x: 0, height: 'auto' }}
              exit={{ opacity: 0, x: 12 }}
              transition={{
                type: 'spring',
                stiffness: 500,
                damping: 35,
                delay: index * 0.05
              }}
              className="flex items-center gap-3 py-2"
            >
              <motion.div
                animate={{
                  color: config.color,
                  rotate: task.status === 'in-progress' ? 360 : 0
                }}
                transition={{
                  rotate: { repeat: Infinity, duration: 1, ease: 'linear' }
                }}
              >
                <Icon size={14} />
              </motion.div>

              <motion.span
                animate={{ color: task.status === 'in-progress' ? 'var(--text-main)' : 'var(--text-dim)' }}
                className="text-sm"
              >
                {task.description}
              </motion.span>
            </motion.div>
          );
        })}
      </AnimatePresence>
    </div>
  );
}
```

### Step 3.6: Results List (`src/renderer/components/ResultsList.jsx`)

```jsx
import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { FileText, Folder, File } from 'lucide-react';
import path from 'path';

function getFileIcon(filePath) {
  const ext = path.extname(filePath).toLowerCase();
  if (!ext) return Folder;
  if (['.txt', '.md', '.py', '.js', '.json', '.html', '.css'].includes(ext)) return FileText;
  return File;
}

function getFileColor(filePath) {
  const ext = path.extname(filePath).toLowerCase();
  const colors = {
    '.py': '#3B82F6',
    '.js': '#F59E0B',
    '.json': '#10B981',
    '.md': '#8B5CF6',
    '.txt': '#9CA3AF',
    '.html': '#EF4444',
    '.css': '#06B6D4',
  };
  return colors[ext] || '#9CA3AF';
}

export default function ResultsList({ items, onSelect }) {
  const [selectedIndex, setSelectedIndex] = useState(-1);

  return (
    <div className="space-y-1.5 py-3">
      {items.slice(0, 5).map((filePath, index) => {
        const Icon = getFileIcon(filePath);
        const color = getFileColor(filePath);
        const basename = path.basename(filePath);
        const isSelected = selectedIndex === index;

        return (
          <motion.button
            key={filePath}
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.06, type: 'spring', stiffness: 400, damping: 25 }}
            whileHover={{ scale: 1.01, x: 4 }}
            whileTap={{ scale: 0.99 }}
            onClick={() => onSelect(filePath)}
            onMouseEnter={() => setSelectedIndex(index)}
            className="w-full text-left p-3 rounded-xl transition-all cursor-pointer group"
            style={{
              background: isSelected
                ? 'rgba(59, 130, 246, 0.08)'
                : 'transparent',
              border: isSelected
                ? '1px solid rgba(59, 130, 246, 0.15)'
                : '1px solid transparent'
            }}
          >
            <div className="flex items-center gap-3">
              <div
                className="p-2 rounded-lg"
                style={{ background: `${color}15`, color }}
              >
                <Icon size={18} />
              </div>

              <div className="flex-1 min-w-0">
                <div className="text-sm font-semibold text-[var(--text-main)] truncate group-hover:text-[var(--accent)] transition-colors">
                  {basename}
                </div>
                <div className="text-xs text-[var(--text-dim)] truncate mt-0.5">
                  {filePath}
                </div>
              </div>
            </div>
          </motion.button>
        );
      })}
    </div>
  );
}
```

### Step 3.7: Mode Toggle (`src/renderer/components/ModeToggle.jsx`)

```jsx
import { motion } from 'framer-motion';

export default function ModeToggle({ mode, onToggle }) {
  const isAuto = mode === 'Auto';

  return (
    <motion.button
      onClick={onToggle}
      whileHover={{ scale: 1.05 }}
      whileTap={{ scale: 0.95 }}
      className="relative px-3 py-1.5 rounded-lg text-xs font-bold cursor-pointer select-none shrink-0"
      style={{
        color: 'var(--accent)',
        background: 'rgba(59, 130, 246, 0.1)',
        border: '1px solid rgba(59, 130, 246, 0.2)'
      }}
    >
      <motion.span
        key={mode}
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.15 }}
      >
        {mode}
      </motion.span>
    </motion.button>
  );
}
```

### Step 3.8: Action Bar (`src/renderer/components/ActionBar.jsx`)

```jsx
import { motion } from 'framer-motion';
import { Zap } from 'lucide-react';

export default function ActionBar({ onExecute }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: 20 }}
      className="px-5 py-4 shrink-0"
      style={{ borderTop: '1px solid var(--border-color)' }}
    >
      <motion.button
        whileHover={{ scale: 1.02 }}
        whileTap={{ scale: 0.98 }}
        onClick={onExecute}
        className="ml-auto flex items-center gap-2 px-5 py-2.5 rounded-xl text-sm font-bold text-white cursor-pointer"
        style={{
          background: 'linear-gradient(135deg, var(--accent), #2563EB)',
          boxShadow: '0 4px 20px rgba(59, 130, 246, 0.3)'
        }}
      >
        <Zap size={16} />
        Execute Plan
      </motion.button>
    </motion.div>
  );
}
```

---

## 6. Phase 4: Python Backend Integration

### Step 4.1: HTTP Server Wrapper

Create `src/main/server_wrapper.py` — this wraps your existing backend:

```python
"""
CursorOS HTTP Server Wrapper
Exposes the existing backend via a local HTTP API for Electron.
"""
import os
import sys
import json
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from backend.core.agent import Agent
from backend.core.os_context import get_open_explorer_windows, read_file_content
from backend.core.llm import llm_service
from backend.tasks.organise_folder import OrganiseFolderTask
from backend.tasks.find_file import FindFileTask


class CursorOSHandler(BaseHTTPRequestHandler):
    """HTTP request handler that bridges Electron → Python backend."""

    agent = None
    current_plan = {"actions": [], "context": {}}
    event_queue = []  # Events to push to Electron via polling

    def do_GET(self):
        parsed = urlparse(self.path)

        if parsed.path == '/api/status':
            self._json_response({"status": "ok", "version": "2.0.0"})

        elif parsed.path == '/api/events':
            # Long-polling endpoint for backend → frontend events
            events = self.event_queue.copy()
            self.event_queue.clear()
            self._json_response({"events": events})

        else:
            self._json_response({"error": "Not found"}, 404)

    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        body = json.loads(self.rfile.read(content_length)) if content_length else {}
        parsed = urlparse(self.path)

        if parsed.path == '/api/submit':
            self._handle_submit(body)
        elif parsed.path == '/api/execute':
            self._handle_execute()
        elif parsed.path == '/api/confirm-org':
            self._handle_confirm_org(body)
        elif parsed.path == '/api/open-file':
            self._handle_open_file(body)
        else:
            self._json_response({"error": "Not found"}, 404)

    def _handle_submit(self, body):
        text = body.get('text', '')
        mode = body.get('mode', 'Auto')

        # Run in background thread
        thread = threading.Thread(
            target=self._process_query,
            args=(text, mode),
            daemon=True
        )
        thread.start()

        self._json_response({"status": "processing"})

    def _process_query(self, text, mode):
        """Background processing — same logic as your current on_submit."""
        self._emit_event({"type": "task_step", "id": "plan", "description": "Generating Plan"})
        self._emit_event({"type": "task_status", "id": "plan", "status": "in-progress"})

        try:
            context = {"explorer_windows": get_open_explorer_windows()}
            plan = self.agent.think(text, context)
            actions = plan.get("actions", [])

            self.current_plan["actions"] = actions
            self._emit_event({"type": "task_status", "id": "plan", "status": "completed"})

            if mode == "Plan":
                self._emit_event({"type": "plan_ready"})
            else:
                self._execute_actions(actions, text)

        except Exception as e:
            print(f"Planning Error: {e}")
            self._emit_event({"type": "task_status", "id": "plan", "status": "failed"})

    def _execute_actions(self, actions, user_text):
        """Execute action chain — same logic as your current execute_action_chain."""
        last_result_path = None

        for i, action_item in enumerate(actions):
            action = action_item.get("action")
            params = action_item.get("params", {})
            explanation = action_item.get("explanation", "Working...")

            task_id = f"task_{i}"
            self._emit_event({"type": "task_step", "id": task_id, "description": explanation})
            self._emit_event({"type": "task_status", "id": task_id, "status": "in-progress"})

            try:
                if action == "find_file":
                    search_desc = params.get("description") or user_text
                    task = FindFileTask()
                    results, msg = task.run(search_desc)
                    if results:
                        last_result_path = results[0]
                        self._emit_event({"type": "results", "items": results})
                    else:
                        raise Exception(f"Could not find '{search_desc}'")

                elif action == "organise_folder":
                    path = params.get("path") or last_result_path
                    if not path:
                        raise Exception("No path provided.")
                    task = OrganiseFolderTask()
                    proposal, err = task.propose(path)
                    if err:
                        raise Exception(err)
                    self._emit_event({"type": "org_preview", "proposal": proposal})

                elif action == "open_path":
                    path = params.get("path") or last_result_path
                    if path:
                        import os
                        os.startfile(path)
                        self._emit_event({"type": "hide"})

                elif action == "chat":
                    message = params.get("message", "...")
                    self._emit_event({"type": "message", "text": message})

                self._emit_event({"type": "task_status", "id": task_id, "status": "completed"})

            except Exception as e:
                print(f"Action failed: {e}")
                self._emit_event({"type": "task_status", "id": task_id, "status": "failed"})
                break

    def _handle_execute(self):
        """Execute the current plan (Plan mode)."""
        actions = self.current_plan.get("actions", [])
        threading.Thread(
            target=self._execute_actions,
            args=(actions, ""),
            daemon=True
        ).start()
        self._json_response({"status": "executing"})

    def _handle_confirm_org(self, body):
        """Handle organization confirmation."""
        # Implementation for confirmed org plan
        self._json_response({"status": "confirmed"})

    def _handle_open_file(self, body):
        path = body.get('path', '')
        if path:
            import os
            os.startfile(path)
        self._json_response({"status": "ok"})

    def _emit_event(self, event):
        """Queue an event for the renderer to pick up."""
        self.event_queue.append(event)

    def _json_response(self, data, status=200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def log_message(self, format, *args):
        """Suppress default HTTP logging noise."""
        pass


def main():
    port = int(os.environ.get('CURSOROS_HTTP_PORT', 9182))

    # Initialize the agent
    CursorOSHandler.agent = Agent()

    server = HTTPServer(('localhost', port), CursorOSHandler)
    print(f'SERVER_READY — CursorOS HTTP server on port {port}', flush=True)
    server.serve_forever()


if __name__ == '__main__':
    main()
```

---

## 7. Phase 5: System Tray & Global Hotkeys

### Step 5.1: Tray Manager (`src/main/tray-manager.js`)

```javascript
const { Tray, Menu, nativeImage } = require('electron');
const path = require('path');

class TrayManager {
  constructor({ onActivate, onQuit }) {
    // Create a simple icon (or load from file)
    const iconPath = path.join(__dirname, '..', '..', 'assets', 'tray-icon.png');
    const icon = nativeImage.createFromPath(iconPath);
    // Resize for tray (16x16 on Windows)
    this.tray = new Tay(icon.resize({ width: 16, height: 16 }));

    this.tray.setToolTip('CursorOS — Press Ctrl+Shift+Space');

    const contextMenu = Menu.buildFromTemplate([
      { label: 'Show CursorOS', click: onActivate },
      { type: 'separator' },
      { label: 'Quit', click: onQuit }
    ]);

    this.tray.setContextMenu(contextMenu);
    this.tray.on('double-click', onActivate);
  }
}

module.exports = TrayManager;
```

### Step 5.2: Global Hotkey Manager (`src/main/hotkey-manager.js`)

```javascript
const { globalShortcut } = require('electron');

class HotkeyManager {
  constructor({ onActivate }) {
    // Register Ctrl+Shift+Space (same as your current keyboard hook)
    const registered = globalShortcut.register('CommandOrControl+Shift+Space', () => {
      console.log('Global hotkey activated');
      onActivate();
    });

    if (!registered) {
      console.error('Failed to register global hotkey');
    }
  }
}

module.exports = HotkeyManager;
```

---

## 8. Phase 6: Transparency & Window Management

### Critical Electron Transparency Settings

This is where your previous `pywebview` attempt failed. Here's the correct way:

```javascript
// In window-manager.js — these settings are CRITICAL for Windows transparency:

const window = new BrowserWindow({
  // ── Transparency ──
  transparent: true,
  frame: false,
  hasShadow: false,

  // ── Windows-specific: prevents the "white box" bug ──
  backgroundColor: '#00000000',  // ARGB — fully transparent

  // ── IMPORTANT: These prevent Windows from disabling transparency ──
  thickFrame: false,  // Prevents WM_NCCALCSIZE which breaks transparency
  webPreferences: {
    // ── GPU acceleration is REQUIRED for smooth transparency ──
    webgl: true,
    offscreen: false
  }
});

// ── Disable Windows DWM composition bypass ──
// Without this, Windows may force opaque background
webContents.setBackgroundThrottle(false);
```

### CSS for Transparency

```css
/* In your renderer CSS — the body MUST be transparent */
html, body, #root {
  background: transparent !important;
}

/* Only the glass-panel gets the semi-opaque background */
.glass-panel {
  background: rgba(13, 13, 14, 0.85);
  backdrop-filter: blur(24px);
}
```

### Windows-Specific Gotcha: GPU Transparency

If you see a white/black background instead of transparency:

```javascript
// Add to the top of index.js, BEFORE app.ready:
app.commandLine.appendSwitch('disable-gpu-compositing', '0');
app.commandLine.appendSwitch('enable-transparent-visuals', '1');

// If still broken, try:
app.disableHardwareAcceleration();  // Last resort — uses CPU compositing
```

---

## 9. Phase 7: Packaging & Distribution

### Step 9.1: electron-builder Configuration

```json
// In package.json
{
  "build": {
    "appId": "com.cursoros.app",
    "productName": "CursorOS",
    "asar": true,
    "win": {
      "target": ["nsis", "portable"],
      "icon": "assets/icon.ico",
      "certificateFile": null,
      "signingHashAlgorithms": ["sha256"]
    },
    "nsis": {
      "oneClick": false,
      "allowToChangeInstallationDirectory": true,
      "createDesktopShortcut": true,
      "createStartMenuShortcut": true,
      "shortcutName": "CursorOS",
      "installerIcon": "assets/icon.ico",
      "uninstallerIcon": "assets/icon.ico",
      "license": "LICENSE"
    },
    "extraResources": [
      {
        "from": "backend/",
        "to": "backend/",
        "filter": ["**/*", "!venv/", "!__pycache__/"]
      }
    ],
    "files": [
      "src/main/**/*",
      "src/preload/**/*",
      "build/renderer/**/*",
      "assets/**/*"
    ]
  }
}
```

### Step 9.2: Bundle Python with the App

**Option A: PyInstaller (Recommended)**

```bash
# Create a standalone Python executable
cd backend
pyinstaller --onefile --name cursoros-backend `
  --hidden-import=backend.core.agent `
  --hidden-import=backend.core.llm `
  --hidden-import=backend.core.os_context `
  --hidden-import=backend.tasks.organise_folder `
  --hidden-import=backend.tasks.find_file `
  --hidden-import=win32com.client `
  ../cursoros-electron/src/main/server_wrapper.py
```

Then in `python-bridge.js`, spawn the `.exe` instead of `python.exe`.

**Option B: Embed Python (python-embed)**

Download the embeddable Python package and bundle it with your app. This avoids requiring users to have Python installed.

### Step 9.3: Build Commands

```bash
# Development
npm run start

# Build for distribution
npm run build

# Create installer
npm run dist
```

---

## 10. Design System & Aesthetics

### Visual Comparison: Tkinter vs. Electron

| Feature | Tkinter (Current) | Electron (Target) |
|---|---|---|
| **Background** | Solid `#0D0D0E` | `rgba(13,13,14,0.85)` + `backdrop-filter: blur(24px)` |
| **Borders** | 1px solid, no radius | 1px + `border-radius: 16px` + glow shadow |
| **Animations** | Manual geometry math | Framer Motion spring physics |
| **Icons** | Unicode characters | Lucide SVG icons (crisp at any size) |
| **Fonts** | System default | Segoe UI with antialiasing |
| **Scrollbars** | ttk.Scrollbar (ugly) | Custom CSS scrollbar |
| **Loading states** | Color change only | Spinner + shimmer skeleton |
| **Hover effects** | None | Scale + color transition |
| **Task list** | Static labels | Staggered entrance animations |
| **Results** | Plain text rows | Icon + colored cards with hover glow |

### Enhanced Design Ideas

Once you're on Electron, you can easily add:

1. **Particle background** — subtle floating particles using `react-particles`
2. **Typing animation** — text appears character-by-character for AI responses
3. **Sound effects** — subtle UI sounds using Web Audio API
4. **Theme switching** — dark/light mode with CSS variables
5. **Micro-interactions** — button ripples, card lifts, smooth page transitions
6. **Rich markdown rendering** — for AI responses with code blocks, lists, etc.
7. **File preview thumbnails** — show image previews, file type badges
8. **Command palette** — VS Code-style command suggestions as you type

### Example: Enhanced Glass Effect

```css
/* Ultra-glass effect */
.ultra-glass {
  background: linear-gradient(
    135deg,
    rgba(13, 13, 14, 0.7) 0%,
    rgba(22, 22, 24, 0.8) 100%
  );
  backdrop-filter: blur(32px) saturate(1.6) brightness(1.1);
  -webkit-backdrop-filter: blur(32px) saturate(1.6) brightness(1.1);
  border: 1px solid rgba(255, 255, 255, 0.06);
  box-shadow:
    0 0 0 1px rgba(59, 130, 246, 0.06),
    0 4px 24px rgba(0, 0, 0, 0.4),
    0 0 80px rgba(59, 130, 246, 0.04),
    inset 0 1px 0 rgba(255, 255, 255, 0.04);
}
```

---

## 11. Troubleshooting & Gotchas

### Common Issues

| Problem | Cause | Solution |
|---|---|---|
| White background instead of transparent | Windows DWM issue | Set `backgroundColor: '#00000000'`, enable GPU |
| Window flickers on show | Double-buffering | Use `show: false` initially, then `show()` |
| Hotkey not working | Another app stole it | Try different hotkey, check with `globalShortcut.isRegistered()` |
| Python process doesn't start | Wrong path | Use `path.join()` with `__dirname`, check `python.exe` exists |
| IPC messages not received | contextBridge misconfig | Ensure `contextIsolation: true`, `nodeIntegration: false` |
| Blurry text on HiDPI | DPI scaling | Add `app.commandLine.appendSwitch('high-dpi-support', '1')` |
| Slow animations | GPU disabled | Ensure `webgl: true` in webPreferences |
| Python stdout not visible | stdio not piped | Use `stdio: ['pipe', 'pipe', 'pipe']` in spawn |
| App appears in taskbar | Missing flag | Set `skipTaskbar: true` |
| Window can't be moved | Frameless | Implement drag via `-webkit-app-region: drag` on header |

### Performance Tips

1. **Use `will-change: transform`** on animated elements
2. **Debounce** the backend polling (don't poll faster than 200ms)
3. **Lazy load** heavy components (OrgPreview, ResultsList)
4. **Use `React.memo`** on list items to prevent unnecessary re-renders
5. **Keep the Python process warm** — don't restart it per query

### Security Considerations

1. **Never enable `nodeIntegration: true`** in the renderer
2. **Always use `contextBridge`** for IPC
3. **Validate all data** from Python before rendering (prevent XSS)
4. **Bind Python server to `localhost`** only — never `0.0.0.0`
5. **Sanitize file paths** before passing to `os.startfile()`

---

## 📅 Suggested Migration Timeline

| Week | Focus | Deliverable |
|---|---|---|
| **Week 1** | Phase 1-2: Scaffold + Main process | Electron app opens, transparent window works |
| **Week 2** | Phase 3: Basic renderer UI | Input bar + mode toggle matching current Tkinter look |
| **Week 3** | Phase 4: Python bridge | Queries flow: Input → Python → Results displayed |
| **Week 4** | Phase 5-6: Polish | Tray, hotkeys, animations, transparency perfected |
| **Week 5** | Phase 7: Package | Installer builds, Python bundled, tested on clean Windows |
| **Week 6** | Enhancements | Glassmorphism, sound, themes, rich previews |

---

## 🔑 Key Takeaway

> **You're NOT rewriting CursorOS.** You're replacing **one file** — `frontend/overlay/window.py` (404 lines of Tkinter) — with a React + Electron frontend. Your entire Python backend (`backend/core/`, `backend/tasks/`, `backend/main.py`) stays intact. The Electron main process simply spawns your Python code as a child process and communicates via HTTP.

The result: the same CursorOS you've built, but with a **stunning, GPU-accelerated, glassmorphic UI** that feels like a modern AI product.

---

*End of Migration Guide — Generated for CursorOS v2.0*
