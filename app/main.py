from typing import List
from fastapi import FastAPI, UploadFile, File, HTTPException
from pathlib import Path
import uuid
import db

TRIGGER_DIR = Path("tasks/incoming")
TRIGGER_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI()
db.init_db()


def _get_file_names(files):
    filenames = [f.filename for f in files]
    filenames_count = {}
    filenames_output = []

    for f in filenames:
        if f in filenames_count:
            filenames_count[f] = filenames_count[f] + 1
        else:
            filenames_count[f] = 0
        filenames_output.append(f"{f}{'_('+str(filenames_count[f])+')' if filenames_count.get(f) else ''}")
    return filenames_output

# Start a new analysis process
@app.post("/process/start")
async def start_task(files: List[UploadFile] = File(...)):
    process_id = uuid.uuid4().hex
    process_path = Path( f"{TRIGGER_DIR}/{process_id}/")
    process_path.mkdir(parents=True, exist_ok=True)
    file_names = _get_file_names(files)

    results = []
    filename_order = 0
    for file in files:
        content = await file.read()
        results.append({
            "filename": process_path / f"{file_names[filename_order]}",
            "size": len(content),
            "content_type": file.content_type,
            "text": content.decode("utf-8")
        })
        filename_order+=1

    for r in results:
        r["filename"].write_text(r["text"])

    db.create_process(process_id, len(files))
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
        if process.status in [db.EnumStatus.COMPLETED.value,db.EnumStatus.RUNNING.value]:
            return db.get_results(process_id)
        elif process.status in [db.EnumStatus.PENDING.value]:
            raise HTTPException(status_code=202,
                                detail=f"Process is in state {process.status}, result is not yet available ")
        elif process.status in [db.EnumStatus.STOPPED.value, db.EnumStatus.FAILED]:
            return {"detail": f"Error: Process finished with state {process.status}"}
        else:
            raise HTTPException(status_code=500,
                                detail=f"Unknown state of the process")
    else:
        raise HTTPException(status_code=404, detail="Process not found")
