import asyncio
import uuid
from pathlib import Path
import db
from document_processing import process_text


TRIGGER_DIR = Path("tasks/incoming")
db.init_db()


async def process_file(p):
    try:
        process_id = p.id
        file_path = TRIGGER_DIR / process_id
        if not file_path.exists():
            print(f"[DAEMON] Process not found: {process_id}")
            db.status_update(process_id, db.EnumStatus.FAILED.value)
            return

        print(f"[DAEMON] Processing: {process_id}")
        db.status_update(process_id, db.EnumStatus.RUNNING.value)
        for f in file_path.iterdir():
            print(f"[DAEMON] Process {process_id} - file {f.name}...")
            content = f.read_text()
            result = process_text(content)
            result.id = uuid.uuid4().hex
            result.process_id = p.id
            result.file_name = f.name
            print(f"[DAEMON] writing result for: {process_id} and file {f.name}")
            db.write_result(result)

        db.status_update(process_id, db.EnumStatus.COMPLETED.value)
        print(f"[DAEMON] Marked as done: {process_id}")
    except Exception as ex:
        print(f"[DAEMON] error - {ex}")
        db.status_update(p.id, db.EnumStatus.FAILED.value)

async def run_daemon():
    print("[DAEMON] Watching DB for pending files...")
    while True:
        pending = db.get_pending_processes()
        for p in pending:
            asyncio.create_task(process_file(p))
        await asyncio.sleep(3)


if __name__ == "__main__":
    asyncio.run(run_daemon())
