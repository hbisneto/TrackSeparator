const { app, BrowserWindow, ipcMain, dialog } = require('electron');
const { spawn } = require('child_process');
const path = require('path');
const axios = require('axios');
const fs = require('fs');

let mainWindow;
let pythonProcess;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 992,
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

ipcMain.handle('get-audio-bitrate', async (event, filePath) => {
  try {
    if (!fs.existsSync(filePath)) {
      throw new Error('File not found');
    }
    
    return new Promise((resolve, reject) => {
      const ffprobe = spawn('ffprobe', [
        '-v', 'quiet',
        '-print_format', 'json',
        '-show_format', filePath
      ]);
      
      let output = '';
      ffprobe.stdout.on('data', (data) => {
        output += data.toString();
      });
      
      ffprobe.stderr.on('data', (data) => {
        console.error(`ffprobe stderr: ${data}`);
      });
      
      ffprobe.on('close', (code) => {
        if (code !== 0) {
          reject(new Error(`ffprobe failed with code ${code}`));
          return;
        }
        
        try {
          const info = JSON.parse(output);
          console.log('ffprobe output:', info);
          const bitrate = info.format.bit_rate ? `${(parseInt(info.format.bit_rate) / 1000).toFixed(0)}` : 'Unknown';
          const sampleRate = info.format.sample_rate ? `${info.format.sample_rate} Hz` : 'Unknown';
          const duration = info.format.duration ? `${parseFloat(info.format.duration).toFixed(2)}` : 'Unknown';
          
          resolve({
            bitrate,
            sampleRate,
            duration
          });
        } catch (parseErr) {
          reject(new Error(`Failed to parse ffprobe output: ${parseErr.message}`));
        }
      });
    });
  } catch (error) {
    console.error('Metadata error:', error);
    throw new Error(`Failed to read metadata: ${error.message}`);
  }
});