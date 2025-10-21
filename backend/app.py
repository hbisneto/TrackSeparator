# -*- coding: utf-8 -*-
from fastapi import FastAPI, WebSocket, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import os
import asyncio
import queue
from soundtrack import separate  # Import do módulo

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

    if not os.path.exists(input_path):
        return JSONResponse(content={"error": "Input file not found"}, status_code=400)
    os.makedirs(output_dir, exist_ok=True)

    try:
        progress_queue = queue.Queue()
        
        async def run_separation():
            await asyncio.to_thread(separate, input_path, output_dir, track=track, progress_queue=progress_queue)
        
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
        
        output_path_track = os.path.join(output_dir, f"{track}.wav")
        output_path_instrumental = os.path.join(output_dir, "instrumental.wav")
        
        if os.path.exists(output_path_track):
            return JSONResponse(content={
                "success": True, 
                "output_file_track": output_path_track,
                "output_file_instrumental": output_path_instrumental
            })
        else:
            return JSONResponse(content={"error": f"Track '{track}' not generated"}, status_code=500)

    except Exception as e:
        print(f"Exception: {e}")
        return JSONResponse(content={"error": str(e)}, status_code=500)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)