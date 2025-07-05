import sqlite3
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Optional

from pydantic import BaseModel

DB_PATH = Path("tasks/data.db")

class Process(BaseModel):
    id: str
    status: str
    created_at: Optional[datetime] = None


class EnumStatus(Enum):
	PENDING = "pending"
	RUNNING = "running"
	PAUSED = "paused"
	COMPLETED = "completed"
	FAILED = "failed"
	STOPPED = "stopped"


def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS process (
            id TEXT PRIMARY KEY,
            status TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()


def create_process(process_id):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(f"INSERT INTO process (id, status) VALUES (?, ?)", (process_id, EnumStatus.PENDING.value))
    conn.commit()
    conn.close()


def get_pending_processes():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM process WHERE status = '{EnumStatus.PENDING.value}'")
    rows = cur.fetchall()
    conn.close()
    return mapping(rows)


def status_update(process_id, status):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(f"UPDATE process SET status = '{status}' WHERE id = ?", (process_id,))
    conn.commit()
    conn.close()


def get_process(process_id):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM process where id = ?", (process_id,))
    rows = cur.fetchall()
    conn.close()
    return mapping(rows)

def get_process_list():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM process")
    rows = cur.fetchall()
    conn.close()
    return mapping(rows)


def mapping(rows):
    if rows:
        return [Process(id=x[0], status=x[1], created_at=x[2]) for x in rows]
    return []