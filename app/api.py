from typing import List
from fastapi import FastAPI, UploadFile, File, HTTPException
from pathlib import Path
import uuid
import db
import models
from config import TRIGGER_DIR, get_logger

_logger = get_logger("API")
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
    _logger.info(f"Starting new process with ID={process_id}")

    try:
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

        num_files = len(files)
        db.create_process(process_id, num_files)

        task_ready_message = "Files written and task queued"
        _logger.info(f"{task_ready_message} PROCCESS_ID: {process_id} NUMBER OF FILES: {num_files}")
        return {"message": "Files written and task queued", "process_id": process_id}
    except Exception as ex:
        _logger.error(f"Error creating new process {process_id} - {ex}")
        raise HTTPException(status_code=500,
                            detail=f"Error creating new process")


# Stop a specific process
@app.post("/process/stop/{process_id}")
def stop_task(process_id):
    _logger.info(f"Attempt to stop process with ID={process_id}")
    try:
        process_list = db.get_process(process_id)
        if process_list:
            process = process_list[0]
            if process.status in [models.EnumStatus.PENDING.value, models.EnumStatus.RUNNING.value]:
                db.status_update(process_id, models.EnumStatus.STOPPED.value)
                _logger.info(f"Process {process_id} stopped")
                return {"message": "Process stopped", "process_id": process_id}
            else:
                _logger.error(f"Process {process_id} is in state {process.status} and cannot be stopped")
                raise HTTPException(status_code=409, detail=f"Process is in state {process.status} and cannot be stopped")
        else:
            _logger.error(f"Process {process_id} not found")
            raise HTTPException(status_code=404, detail="Process not found")
    except HTTPException:
        raise
    except Exception as ex:
        _logger.error(f"Error stopping process - {process_id} - {ex}")
        raise HTTPException(status_code=500, detail="Internal server error")



# Query the status of a process
@app.get("/process/status/{process_id}")
def stop_task(process_id):
    _logger.info(f"Getting status of process: {process_id}")
    try:
        process_list = db.get_process(process_id)
        if process_list:
            process = process_list[0]
            _logger.info(f"Status of process: {process_id} is {process.status}")
            return process.model_dump()
        else:
            _logger.error(f"Process: {process_id} not found")
            raise HTTPException(status_code=404, detail="Process not found")
    except HTTPException:
        raise
    except Exception as ex:
        _logger.error(f"Error getting status for proccess {process_id} - {ex}")
        raise HTTPException(status_code=500, detail="Internal server error")


# List all processes and their states
@app.get("/process/list")
def stop_task():
    _logger.info(f"Getting list of process")
    try:
        process_list = db.get_process_list()
        process_list_output = [x.model_dump() for x in process_list]
        return process_list_output
    except Exception as ex:
        _logger.error(f"Error getting process list - {ex}")
        raise HTTPException(status_code=500, detail="Internal server error")


# Get analysis results
@app.get("/process/reseults/{process_id}")
def stop_task(process_id):
    _logger.info(f"Getting results for process {process_id}")
    try:
        process_list = db.get_process(process_id)
        if process_list:
            process = process_list[0]
            if process.status in [models.EnumStatus.COMPLETED.value,models.EnumStatus.RUNNING.value]:
                result_out = db.get_results(process_id)
                _logger.info(f"Success returning results for process {process_id}")
                return result_out
            elif process.status in [models.EnumStatus.PENDING.value]:
                _logger.error(f"Process {process_id} is in state {process.status}, result is not yet available ")
                raise HTTPException(status_code=202,
                                    detail=f"Process is in state {process.status}, result is not yet available ")
            elif process.status in [models.EnumStatus.STOPPED.value, models.EnumStatus.FAILED.value]:
                _logger.error(f"Error: Process {process_id} finished with state {process.status}")
                return {"detail": f"Error: Process finished with state {process.status}"}
            else:
                _logger.error(f"Unknown state of the process {process_id}")
                raise HTTPException(status_code=500,
                                    detail=f"Unknown state of the process")
        else:
            _logger.error(f"Process {process_id} not found")
            raise HTTPException(status_code=404, detail="Process not found")
    except HTTPException:
        raise
    except Exception as ex:
        _logger.error(f"Error getting results for process {process_id} - {ex}")
        raise HTTPException(status_code=500, detail="Internal server error")
