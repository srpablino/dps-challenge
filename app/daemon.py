import asyncio
import logging
import uuid
import db
from document_processing import process_text
from config import get_logger, TRIGGER_DIR

_logger = get_logger("DAEMON")
db.init_db()


def update_process_status(p):
    try:
        process_id = p.id
        file_path = TRIGGER_DIR / process_id
        if not file_path.exists():
            _logger.error(f"Process not found: {process_id}")
            db.status_update(process_id, db.EnumStatus.FAILED.value)
            return

        _logger.info(f"Processing: {process_id}")
        db.status_update(process_id, db.EnumStatus.RUNNING.value)
    except Exception as ex:
        _logger.error(f"error - {ex}")
        db.status_update(p.id, db.EnumStatus.FAILED.value)


def _process_status_running(process_id):
    process = db.get_process(process_id)
    if not process or process[0].status != db.EnumStatus.RUNNING.value:
        state = process[0].status if process else "UNKNOWN"
        _logger.error(f"Process can't continue, the status has ben externally updataed to {state}")
        return False
    return True


async def process_file(p):
    try:
        process_id = p.id
        file_path = TRIGGER_DIR / process_id
        process_running = True
        for f in file_path.iterdir():
            _logger.info(f"Processing {process_id} - file {f.name}...")
            content = f.read_text()
            result = await asyncio.to_thread(process_text, content)
            result.id = uuid.uuid4().hex
            result.process_id = p.id
            result.file_name = f.name
            _logger.info(f"Writing result for: {process_id} and file {f.name}")
            if await asyncio.to_thread(_process_status_running, process_id):
                await asyncio.to_thread(db.write_result, result)
            else:
                process_running = False
                break

        if process_running:
            await asyncio.to_thread(db.status_completed, process_id)
        else:
            return

        _logger.info(f"Marked as done: {process_id}")
    except Exception as ex:
        _logger.error(f"error - {ex}")
        await asyncio.to_thread(db.status_update,p.id, db.EnumStatus.FAILED.value)

async def run_daemon():
    iteration = 0
    while True:
        if iteration % 12 == 0:
            _logger.info("Watching DB for pending files...")
            iteration = 0
        pending = await asyncio.to_thread(db.get_pending_processes)
        for p in pending:
            await asyncio.to_thread(update_process_status, p)
            asyncio.create_task(process_file(p))
        await asyncio.sleep(5)
        iteration+=1


if __name__ == "__main__":
    asyncio.run(run_daemon())
