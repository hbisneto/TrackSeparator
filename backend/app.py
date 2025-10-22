# -*- coding: utf-8 -*-
from fastapi import FastAPI, WebSocket, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import os
import asyncio
import queue
from soundtrack import separate

app = FastAPI()

class SeparateRequest(BaseModel):
    input_path: str
    output_dir: str
    track: str

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

@app.websocket("/ws/progress")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
    except:
        manager.disconnect(websocket)

@app.post("/separate")
async def separate_track(request: SeparateRequest):
    print(f"Parsed model: {request}")

    input_path = request.input_path
    output_dir = request.output_dir
    track = request.track

    print(f"Input path: {input_path}")
    print(f"File exists: {os.path.exists(input_path)}")
    if os.path.exists(input_path):
        print(f"File size: {os.path.getsize(input_path)} bytes")
        print(f"File readable: {os.access(input_path, os.R_OK)}")
    print(f"Output dir: {output_dir}")

    if not os.path.exists(input_path):
        return JSONResponse(content={"error": "Input file not found"}, status_code=400)
    
    try:
        with open(input_path, 'rb') as f:
            preview = f.read(100)
            print(f"File preview (first 100 bytes): {preview[:50]}...")
    except Exception as open_err:
        print(f"Erro ao abrir arquivo: {open_err}")
        return JSONResponse(content={"error": f"Cannot open file: {str(open_err)}"}, status_code=400)

    os.makedirs(output_dir, exist_ok=True)

    try:
        progress_queue = queue.Queue()
        
        async def run_separation():
            print("Iniciando separate...")
            await asyncio.to_thread(separate, input_path, output_dir, track=track, progress_queue=progress_queue)
            print("Separate finalizado com sucesso.")
        
        separation_task = asyncio.create_task(run_separation())
        
        while True:
            try:
                progress = progress_queue.get_nowait()
                await manager.broadcast(f'{{"progress": {progress}}}')
                await asyncio.sleep(0.1)
            except queue.Empty:
                if separation_task.done():
                    break
                await asyncio.sleep(0.1)
        
        await separation_task
        
        input_basename = os.path.splitext(os.path.basename(input_path))[0]
        output_path_track = os.path.join(output_dir, input_basename, f"{track}.wav")
        output_path_instrumental = os.path.join(output_dir, input_basename, "no_vocals.wav")
        
        print(f"Checando arquivos: track={output_path_track}, instrumental={output_path_instrumental}")
        print(f"Track existe: {os.path.exists(output_path_track)}")
        print(f"Instrumental existe: {os.path.exists(output_path_instrumental)}")
        
        if os.path.exists(output_path_track):
            print(f"Arquivos gerados: {output_path_track}, {output_path_instrumental}")
            return JSONResponse(content={
                "success": True, 
                "output_file_track": output_path_track,
                "output_file_instrumental": output_path_instrumental
            })
        else:
            print(f"Conteúdo da pasta {output_dir}: {os.listdir(output_dir)}")
            return JSONResponse(content={"error": f"Track '{track}' not generated at {output_path_track}"}, status_code=500)

    except Exception as e:
        print(f"Exception na separação: {e}")
        print(f"Traceback completo:\n{traceback.format_exc()}")
        return JSONResponse(content={"error": f"Separation failed: {str(e)}"}, status_code=500)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)