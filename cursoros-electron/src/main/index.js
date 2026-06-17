const { app, ipcMain, globalShortcut } = require('electron');
const path = require('path');
const WindowManager = require('./window-manager');
const TrayManager = require('./tray-manager');
const HotkeyManager = require('./hotkey-manager');
const PythonBridge = require('./python-bridge');

// ── Transparency fix for Windows ──
app.commandLine.appendSwitch('enable-transparent-visuals', '1');
app.commandLine.appendSwitch('high-dpi-support', '1');

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
  // 1. Start Python backend
  pythonBridge = new PythonBridge();
  try {
    await pythonBridge.start();
  } catch (err) {
    console.error('Failed to start Python backend:', err);
  }

  // 2. Create the transparent overlay window
  windowManager = new WindowManager();
  windowManager.create();

  // 3. Setup system tray
  trayManager = new TrayManager({
    onActivate: () => windowManager.toggle(),
    onQuit: () => app.quit(),
  });

  // 4. Register global hotkey via dedicated manager
  hotkeyManager = new HotkeyManager({
    onActivate: () => windowManager.toggle(),
  });

  // 5. IPC handlers for renderer -> main -> python
  ipcMain.handle('backend:submit', async (_, text, mode) => {
    return pythonBridge.call('/api/submit', 'POST', { text, mode });
  });

  ipcMain.handle('backend:execute', async () => {
    return pythonBridge.call('/api/execute', 'POST');
  });

  ipcMain.handle('backend:confirm-org', async (_, proposal) => {
    return pythonBridge.call('/api/confirm-org', 'POST', { proposal });
  });

  ipcMain.handle('backend:open-file', async (_, filePath) => {
    return pythonBridge.call('/api/open-file', 'POST', { path: filePath });
  });

  // 6. Poll Python events and push to renderer
  setInterval(async () => {
    try {
      const result = await pythonBridge.call('/api/events');
      if (result.events && result.events.length > 0) {
        result.events.forEach(event => {
          if (windowManager.window && !windowManager.window.isDestroyed()) {
            windowManager.window.webContents.send('backend:event', event);
          }
        });
      }
    } catch (e) {
      // Silently ignore polling errors
    }
  }, 200);

  console.log('CursorOS Electron is running.');
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit();
});

app.on('will-quit', async () => {
  globalShortcut.unregisterAll();
  if (pythonBridge) await pythonBridge.stop();
});
