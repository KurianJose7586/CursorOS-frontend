const { BrowserWindow, screen } = require('electron');
const path = require('path');

class WindowManager {
  constructor() {
    this.window = null;
    this.isExpanded = false;

    this.collapsedBounds = { width: 100, height: 4 };
    this.expandedBounds = { width: 640, height: 500, y: 60 };
  }

  create() {
    const { width: screenW, height: screenH } = screen.getPrimaryDisplay().workAreaSize;

    this.window = new BrowserWindow({
      width: this.collapsedBounds.width,
      height: this.collapsedBounds.height,
      x: Math.floor((screenW - this.collapsedBounds.width) / 2),
      y: 40,

      frame: false,
      transparent: true,
      hasShadow: false,

      // ── Komorebi compatibility ──
      // skipTaskbar prevents Komorebi from seeing the window,
      // but we need it false so the window can be focused.
      // Instead we use type: "toolbar" to hint window managers.
      skipTaskbar: false,
      alwaysOnTop: true,
      resizable: false,
      movable: false,
      focusable: true,
      show: false,
      backgroundColor: '#00000000',

      // ── Window type hints for tiling WMs ──
      // "toolbar" tells WMs this is a floating utility, not a normal window
      // "splash" is another option that many WMs leave alone
      type: 'toolbar',

      webPreferences: {
        preload: path.join(__dirname, '..', 'preload', 'index.js'),
        contextIsolation: true,
        nodeIntegration: false,
        sandbox: false,
      }
    });

    // ── Komorebi / tiling WM compatibility ──
    // Use screen-saver level to stay above everything including YASB
    this.window.setAlwaysOnTop(true, 'screen-saver');
    this.window.setSkipTaskbar(true);
    this.window.setMinimizable(false);

    // Load the React app
    if (process.env.VITE_DEV_SERVER_URL) {
      this.window.loadURL(process.env.VITE_DEV_SERVER_URL);
    } else {
      this.window.loadFile(path.join(__dirname, '..', '..', 'build', 'renderer', 'index.html'));
    }

    this.window.setContentProtection(true);

    // ── Debug: log window state
    this.window.webContents.on('did-finish-load', () => {
      console.log('[Window] Renderer loaded');
    });

    this.window.on('show', () => {
      console.log('[Window] Shown at:', this.window.getBounds());
    });
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

    this.window.setBounds({
      width: this.collapsedBounds.width,
      height: this.collapsedBounds.height,
      x: Math.floor((screenW - this.collapsedBounds.width) / 2),
      y: 0,
    });

    this.window.show();
    this.window.focus();
    this.window.webContents.send('window:show');
  }

  hide() {
    this.window.webContents.send('window:hide');
    setTimeout(() => {
      if (this.window && !this.window.isDestroyed()) {
        this.window.hide();
      }
      this.isExpanded = false;
    }, 350);
  }

  expandForContent() {
    if (this.isExpanded) return;
    this.isExpanded = true;

    const { width: screenW } = screen.getPrimaryDisplay().workAreaSize;
    this.window.setBounds({
      width: this.expandedBounds.width,
      height: this.expandedBounds.height,
      x: Math.floor((screenW - this.expandedBounds.width) / 2),
      y: this.expandedBounds.y,
    });
  }
}

module.exports = WindowManager;
