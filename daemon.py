import asyncio
from pathlib import Path
from db import init_db, get_pending_processes, status_update, EnumStatus

TRIGGER_DIR = Path("tasks/incoming")
init_db()


async def process_file(process_id):
    file_path = TRIGGER_DIR / process_id
    if not file_path.exists():
        print(f"[DAEMON] Process not found: {process_id}")
        return
    print(f"[DAEMON] Processing: {process_id}")

    for f in file_path.iterdir():
        content = f.read_text()
        print(f"[DAEMON] Content for process {process_id} - file {f.name}: \n {content.strip()}")

    # Do any processing here...
    status_update(process_id, EnumStatus.COMPLETED.value)
    print(f"[DAEMON] Marked as done: {process_id}")


async def run_daemon():
    print("[DAEMON] Watching DB for pending files...")
    while True:
        pending = get_pending_processes()
        for p in pending:
            asyncio.create_task(process_file(p.id))
        await asyncio.sleep(3)


if __name__ == "__main__":
    asyncio.run(run_daemon())
