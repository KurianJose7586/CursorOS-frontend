const { globalShortcut } = require('electron');

class HotkeyManager {
  constructor({ onActivate }) {
    const registered = globalShortcut.register('CommandOrControl+Shift+Space', () => {
      console.log('Global hotkey activated');
      onActivate();
    });

    if (!registered) {
      console.error('Failed to register global hotkey — another app may have claimed it');
    } else {
      console.log('Global hotkey registered: Ctrl+Shift+Space');
    }
  }
}

module.exports = HotkeyManager;
