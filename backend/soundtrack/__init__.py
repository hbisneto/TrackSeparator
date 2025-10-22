# -*- coding: utf-8 -*-
import subprocess
import shutil
import os
import queue

def get_directories(path):
    return [d for d in os.listdir(path) if os.path.isdir(os.path.join(path, d))]

def join(base, *paths):
    return os.path.join(base, *paths)

def exists(path):
    return os.path.exists(path)

def create(path):
    os.makedirs(path, exist_ok=True)

def move(src, dst):
    shutil.move(src, dst)

def delete(path, recursive=False):
    if recursive:
        shutil.rmtree(path)
    else:
        os.remove(path)

def separate(audio_file, output_dir, track="vocals", use_old_model=False, progress_queue=None):
    model = "mdx_extra_q" if use_old_model else "htdemucs"
    command = f'demucs -n {model} --two-stems={track} --out {output_dir} "{audio_file}"'
    print(f"Executando comando: {command}")
    
    process = subprocess.Popen(
        command, shell=True, 
        stdout=subprocess.PIPE, 
        stderr=subprocess.STDOUT,
        text=True, 
        universal_newlines=True,
        bufsize=1
    )
    
    print(f"Processo Demucs iniciado com PID: {process.pid}")
    
    progress = 0
    full_output = ""
    while True:
        output = process.stdout.readline()
        if output == '' and process.poll() is not None:
            break
        if output:
            print(output.strip())
            full_output += output
            if '%' in output and '|' in output:
                try:
                    percent_str = output.split('%')[0].split('|')[-1].strip().replace(' ', '')
                    new_progress = int(percent_str)
                    if 0 <= new_progress <= 100:
                        progress = new_progress
                        if progress_queue:
                            progress_queue.put(progress)
                except ValueError:
                    pass
    
    returncode = process.returncode
    print(f"Demucs terminou com returncode: {returncode}")
    
    if returncode != 0:
        error_msg = f"Demucs failed with code {returncode}. Output: {full_output[:500]}..."
        raise RuntimeError(error_msg)
    
    demucs_output_dir = join(output_dir, "htdemucs")
    if exists(demucs_output_dir):
        for directory in get_directories(demucs_output_dir):
            move(join(demucs_output_dir, directory), output_dir)
        delete(demucs_output_dir, True)
    
    if progress_queue:
        progress_queue.put(100)