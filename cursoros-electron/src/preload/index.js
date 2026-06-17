const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('cursoros', {
  // Window events from main
  onWindowShow: (callback) => ipcRenderer.on('window:show', callback),
  onWindowHide: (callback) => ipcRenderer.on('window:hide', callback),

  // Backend events from Python (pushed via polling)
  onBackendEvent: (callback) => ipcRenderer.on('backend:event', (_, data) => callback(data)),

  // Actions
  submitQuery: (text, mode) => ipcRenderer.invoke('backend:submit', text, mode),
  expandWindow: () => ipcRenderer.send('window:expand'),
  hideWindow: () => ipcRenderer.send('window:hide'),
  executePlan: () => ipcRenderer.invoke('backend:execute'),
  confirmOrg: (proposal) => ipcRenderer.invoke('backend:confirm-org', proposal),
  openFile: (filePath) => ipcRenderer.invoke('backend:open-file', filePath),
});
