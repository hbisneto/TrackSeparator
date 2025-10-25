# TrackSeparator

[![Node.js](https://img.shields.io/badge/Node.js-v22.17-green)](https://nodejs.org/) [![Python](https://img.shields.io/badge/Python-v3.9-blue)](https://python.org/) [![Electron](https://img.shields.io/badge/Electron-v32-red)](https://electronjs.org/)

---

**TrackSeparator** is a desktop application built with **Electron** (frontend) and **Python** (backend) to separate audio tracks into individual stems, such as vocals, drums, bass, or "other" (guitar/instrumental). It uses the **Demucs** library (based on PyTorch) to process audio files (MP3, WAV, FLAC) and generate isolated versions, including the instrumental (without the selected stem).

- **Objective**: Allow musicians, producers, and enthusiasts to separate music elements in a simple way, saving files to the desired folder.
- **Architecture**: Frontend in HTML/JS with Electron for native UI (file/folder dialogs). Backend in FastAPI with subprocess to call the Demucs CLI.
- **Current Version**: 1.0.0 (October 2025).

## Features

- Stem separation: Vocals, drums, bass, or "other" (generates `{stem}.wav` + `instrumental.wav`).
- Simple interface: Buttons to select audio file and output folder.
- Real-time progress: Animated bar with percentage during processing.
- Supported formats: MP3, WAV, FLAC, M4A.
- Standalone: Build as .dmg for macOS (no Python/Node installation required).

## Prerequisites

- **Node.js**: v22.17 or higher (download from [nodejs.org](https://nodejs.org/)).
- **Python**: v3.9 (use Homebrew: `brew install python@3.9`).
- **FFmpeg**: For audio support (install via Homebrew: `brew install ffmpeg`).
- **Git**: To clone the project (if applicable).
- **VS Code** (optional): With "Python" and "Debugger for Electron" extensions.

## Installation

1. Clone the repository (if available):

   ```
   git clone https://github.com/hbisneto/TrackSeparator.git
   cd TrackSeparator
   ```

2. **Backend (Python)**:

   ```
   cd backend
   python3.9 -m venv venv
   source venv/bin/activate  # Activate venv
   pip install -r requirements.txt
   ```

3. **Frontend (Node)**:

   ```
   cd ..  # Back to root
   npm install
   ```

## How to Run

### Via Terminal

1. Activate the backend:

   ```
   cd backend
   source venv/bin/activate
   python app.py  # Runs server at http://localhost:8000
   ```

2. In another terminal, run the frontend:

   ```
   cd TrackSeparator  # Project root
   npm run dev  # Development mode
   ```
   
   - Opens the Electron window. Select file/folder/track and click "Start Separation".
   - The backend processes and saves files to the chosen folder.

3. Stop: Ctrl+C in the backend terminal.

### Via VS Code

1. Open the project in VS Code (`File > Open Folder > TrackSeparator`).

2. **Install Extensions**:
   - "Python" (Microsoft) for venv/debug.
   - "Debugger for Electron" for frontend debug.

3. **Configure Backend**:
   - Open `backend/app.py`.
   - Create `.vscode/launch.json` in the root (or use Run > Add Configuration):

     ```json
     {
       "version": "0.2.0",
       "configurations": [
         {
           "name": "Python: Backend",
           "type": "python",
           "request": "launch",
           "program": "${workspaceFolder}/backend/app.py",
           "console": "integratedTerminal",
           "cwd": "${workspaceFolder}/backend",
           "env": {"PYTHONPATH": "${workspaceFolder}/backend"}
         }
       ]
     }
     ```
     
   - Run: F5 or Run > Start Debugging (select "Python: Backend").

4. **Configure Frontend**:
   - Create `.vscode/tasks.json` in the root:

     ```json
     {
       "version": "2.0.0",
       "tasks": [
         {
           "label": "npm: dev",
           "type": "npm",
           "script": "dev",
           "group": "build",
           "presentation": {"echo": true, "reveal": "always", "focus": false, "panel": "shared"}
         }
       ]
     }
     ```
     
   - Add to `launch.json`:

     ```json
     {
       "name": "Electron: Dev",
       "type": "node",
       "request": "launch",
       "program": "${workspaceFolder}/node_modules/.bin/electron",
       "args": [".", "--remote-debugging-port=9222"],
       "cwd": "${workspaceFolder}",
       "console": "integratedTerminal",
       "preLaunchTask": "npm: dev"
     }
     ```
     
   - Run: F5 (select "Electron: Dev") – opens app with debug (F12 for DevTools).

5. **Joint Debug**: Run backend first (F5 Python), then frontend (F5 Electron). Use breakpoints in VS Code to pause in `separate` or IPC.

## Build and Distribution

1. **Backend Executable** (PyInstaller):

   ```
   cd backend
   source venv/bin/activate
   pyinstaller backend.spec --clean
   ```
   - Generates `dist/app` (standalone ~500MB).

2. **Full App** (Electron Builder):

   ```
   cd TrackSeparator
   npm run build
   ```
   
   - Generates `dist/TrackSeparator-1.0.0.dmg` (installable on macOS).

## Troubleshooting

- **Processing Timeout**: Increase timeout in `main.js` (timeout: 0 for infinite).
- **Demucs Crash**: Check FFmpeg (`ffmpeg -version`). Use short tracks for testing.
- **Progress Not Animating**: Check backend logs (tqdm prints). If queue empty, add prints in separate.
- **422 Error**: Confirm snake_case in JSON (input_path, output_dir).
- **EGL Errors**: Electron bug on Big Sur – ignore; doesn't affect functionality.
- **Memory Issues**: Close apps; Demucs uses ~2GB RAM.

## Contribution

- Fork the repo and send PRs.
- Report issues on GitHub.

## License

MIT License. See [LICENSE](LICENSE).

---

*Project created in October 2025 by Heitor Bisneto.*