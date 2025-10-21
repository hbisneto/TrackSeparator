const { app, BrowserWindow, ipcMain, dialog } = require('electron');
const { spawn } = require('child_process');
const path = require('path');
const axios = require('axios');

let mainWindow;
let pythonProcess;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 800,
    height: 600,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false
    }
  });
  mainWindow.loadFile('frontend/index.html');
}

app.whenReady().then(() => {
  const isProd = process.env.NODE_ENV === 'production';
  const pythonPath = isProd ? path.join(process.resourcesPath, 'backend/dist/app') : 'python';
  const args = isProd ? [] : ['backend/app.py'];

  pythonProcess = spawn(pythonPath, args, { stdio: 'pipe' });

  pythonProcess.stdout.on('data', (data) => console.log(`Backend: ${data}`));
  pythonProcess.stderr.on('data', (data) => console.error(`Erro Backend: ${data}`));
  pythonProcess.on('close', (code) => console.log(`Backend fechado: ${code}`));

  createWindow();
});

app.on('window-all-closed', () => {
  if (pythonProcess) pythonProcess.kill();
  if (process.platform !== 'darwin') app.quit();
});

ipcMain.handle('select-file', async () => {
  const result = await dialog.showOpenDialog(mainWindow, {
    properties: ['openFile'],
    filters: [{ name: 'Audio', extensions: ['mp3', 'wav', 'flac', 'm4a'] }]
  });
  return result;
});

ipcMain.handle('select-folder', async () => {
  const result = await dialog.showOpenDialog(mainWindow, {
    properties: ['openDirectory'],
    title: 'Escolha pasta para salvar'
  });
  return result;
});

ipcMain.handle('separate-track', async (event, params) => {
  try {
    console.log('Received params:', params);
    const response = await axios.post('http://localhost:8000/separate', params, { timeout: 0 });
    return { success: true, ...response.data };
  } catch (error) {
    console.error('Axios error:', error.response?.data || error.message);
    throw new Error(error.response?.data?.error || error.message);
  }
});