from typing import List
from fastapi import FastAPI, UploadFile, File, HTTPException
from pathlib import Path
import uuid
import db

TRIGGER_DIR = Path("tasks/incoming")
TRIGGER_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI()
db.init_db()


# Start a new analysis process
@app.post("/process/start")
async def start_task(files: List[UploadFile] = File(...)):
    process_id = uuid.uuid4().hex
    process_path = Path( f"{TRIGGER_DIR}/{process_id}/")
    process_path.mkdir(parents=True, exist_ok=True)

    results = []
    for file in files:
        file_name = uuid.uuid4().hex
        content = await file.read()
        results.append({
            "filename": process_path / file_name,
            "size": len(content),
            "content_type": file.content_type,
            "text": content.decode("utf-8")
        })

    for r in results:
        r["filename"].write_text(r["text"])

    db.create_process(process_id)
    return {"message": "Files written and task queued", "process_id": process_id}

# Stop a specific process
@app.post("/process/stop/{process_id}")
def stop_task(process_id):
    process_list = db.get_process(process_id)
    if process_list:
        process = process_list[0]
        if process.status in [db.EnumStatus.PENDING.value, db.EnumStatus.RUNNING]:
            db.status_update(process_id, db.EnumStatus.STOPPED.value)
            return {"message": "Process stopped", "process_id": process_id}
        else:
            raise HTTPException(status_code=409, detail=f"Process is in state {process.status} and cannot be stopped")
    else:
        raise HTTPException(status_code=404, detail="Process not found")


# Query the status of a process
@app.get("/process/status/{process_id}")
def stop_task(process_id):
    process_list = db.get_process(process_id)
    if process_list:
        process = process_list[0]
        return process.model_dump()
    else:
        raise HTTPException(status_code=404, detail="Process not found")


# List all processes and their states
@app.get("/process/list")
def stop_task():
    process_list = db.get_process_list()
    process_list_output = [x.model_dump() for x in process_list]
    return process_list_output


# Get analysis results
@app.get("/process/reseults/{process_id}")
def stop_task(process_id):
    process_list = db.get_process(process_id)
    if process_list:
        process = process_list[0]
        if process.status == db.EnumStatus.COMPLETED.value:
            return process.model_dump()
        elif process.status in [db.EnumStatus.RUNNING.value, db.EnumStatus.PENDING.value]:
            raise HTTPException(status_code=202,
                                detail=f"Process is in state {process.status}, result is not yet available ")
        elif process.status in [db.EnumStatus.STOPPED.value, db.EnumStatus.FAILED]:
            return {"detail": f"Error: Process finished with state {process.status}"}
        else:
            raise HTTPException(status_code=500,
                                detail=f"Unknown state of the process")
    else:
        raise HTTPException(status_code=404, detail="Process not found")
