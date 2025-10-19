# -*- coding: utf-8 -*-
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import os
import shutil
from demucs.separate import main

app = FastAPI()

class SeparateRequest(BaseModel):
    input_path: str
    output_dir: str
    stem: str  # vocals, drums, bass, other

@app.post("/separate")
async def separate_track(request: SeparateRequest):
    input_path = request.input_path
    output_dir = request.output_dir
    stem = request.stem

    if not os.path.exists(input_path):
        return JSONResponse(content={"error": "Input file not found"}, status_code=400)
    os.makedirs(output_dir, exist_ok=True)

    try:
        # Valid args: -n for model, -o for output, --float32 for quality
        args = [input_path, '-n', 'htdemucs', '-o', output_dir, '--float32']
        main(args)  # Runs full separation (2-5 min on CPU)

        # Copy only the selected stem to output_dir/{stem}.wav
        stem_dir = os.path.join(output_dir, 'htdemucs', stem)
        if os.path.exists(stem_dir):
            stem_files = [f for f in os.listdir(stem_dir) if f.endswith('.wav')]
            if stem_files:
                source_file = os.path.join(stem_dir, stem_files[0])
                output_path = os.path.join(output_dir, f"{stem}.wav")
                shutil.copy2(source_file, output_path)
                return JSONResponse(content={"success": True, "output_file": output_path})
        return JSONResponse(content={"error": f"Stem '{stem}' not generated"}, status_code=500)

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)