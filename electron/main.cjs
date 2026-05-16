const { app, BrowserWindow } = require('electron');

function createWindow() {
  const win = new BrowserWindow({
    width: 1280,
    height: 860,
    title: 'NextUSinger Studio',
    webPreferences: { nodeIntegration: false, contextIsolation: true },
  });
  win.loadURL(process.env.NEXTUSINGER_FRONTEND_URL || 'http://127.0.0.1:5173');
}

app.whenReady().then(createWindow);
app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit();
});
app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) createWindow();
});
