const { Tray, Menu, nativeImage, nativeTheme } = require('electron');
const path = require('path');

class TrayManager {
  constructor({ onActivate, onQuit }) {
    // Create a simple tray icon programmatically
    const icon = this.createIcon();
    this.tray = new Tray(icon);

    this.tray.setToolTip('CursorOS — ⌘⇧Space to activate');

    const contextMenu = Menu.buildFromTemplate([
      { label: 'Show CursorOS', accelerator: 'Ctrl+Shift+Space', click: onActivate },
      { type: 'separator' },
      { label: 'Quit', role: 'quit', click: onQuit }
    ]);

    this.tray.setContextMenu(contextMenu);
    this.tray.on('double-click', onActivate);
  }

  createIcon() {
    // Create a simple 16x16 icon using a canvas-like approach
    // For now, use a small native image
    const size = 16;
    const canvas = Buffer.alloc(size * size * 4);

    // Fill with a simple blue dot pattern
    for (let y = 0; y < size; y++) {
      for (let x = 0; x < size; x++) {
        const i = (y * size + x) * 4;
        const cx = x - size / 2;
        const cy = y - size / 2;
        const dist = Math.sqrt(cx * cx + cy * cy);

        if (dist < 6) {
          canvas[i] = 10;     // R
          canvas[i + 1] = 132; // G
          canvas[i + 2] = 255; // B
          canvas[i + 3] = 255; // A
        } else {
          canvas[i + 3] = 0;   // Transparent
        }
      }
    }

    const img = nativeImage.createFromBuffer(canvas, { width: size, height: size });
    return img.resize({ width: 16, height: 16 });
  }
}

module.exports = TrayManager;
