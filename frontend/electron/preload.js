const { contextBridge, ipcRenderer } = require('electron')

/**
 * OsintGraph Preload — context bridge
 * Exposes safe APIs to the renderer process via window.osint
 */
contextBridge.exposeInMainWorld('osint', {
  // IPC bridge to FastAPI backend
  api: {
    call: (method, path, body) => ipcRenderer.invoke('api:call', { method, path, body }),
    get: (path) => ipcRenderer.invoke('api:call', { method: 'GET', path }),
    post: (path, body) => ipcRenderer.invoke('api:call', { method: 'POST', path, body }),
    put: (path, body) => ipcRenderer.invoke('api:call', { method: 'PUT', path, body }),
    delete: (path) => ipcRenderer.invoke('api:call', { method: 'DELETE', path }),
  },
  // Platform info
  platform: process.platform,
})
