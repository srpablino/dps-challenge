from typing import List

from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
from pathlib import Path
import uuid
import db

TRIGGER_DIR = Path("tasks/incoming")
TRIGGER_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI()
db.init_db()

# class TaskRequest(BaseModel):
#     message: str

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
            return {"message": f"Process is in state {process.status} and cannot be stopped"}
    else:
        return {"message": f"Process not found"}


# POST /process/start - Start a new analysis process
# POST /process/stop/{process_id} - Stop a specific process
# GET /process/status/{process_id} - Query the status of a process
# GET /process/list - List all processes and their states
# GET /process/results/{process_id} - Get analysis results