import json
import sqlite3
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Optional, List

from pydantic import BaseModel

DB_PATH = Path("tasks/data.db")


class ResultDetailsOut(BaseModel):
    total_words: Optional[int] = 0
    total_lines: Optional[int] = 0
    total_chars: Optional[int] = 0
    most_frequent_words: Optional[dict] = {}
    files_processed: Optional[List[str]] = []
    files_summary: Optional[List[str]] = []

class ProgressOut(BaseModel):
    total_files: Optional[int] = 0
    processed_files: Optional[int] = 0
    percentage: Optional[int] = 0

class ResultOut(BaseModel):
    process_id: Optional[str] = None
    status: Optional[str] = None
    progress: Optional[ProgressOut] = ProgressOut()
    started_at: Optional[datetime] = None
    results: Optional[ResultDetailsOut] = ResultDetailsOut()
    estimated_completion: Optional[datetime] = None


class Result(BaseModel):
    id: Optional[str] = None
    process_id: Optional[str] = None
    file_name: Optional[str] = None
    total_words: Optional[int] = None
    total_lines: Optional[int] = None
    total_chars: Optional[int] = None
    most_frequent_words: Optional[int] = None
    summary: Optional[str] = None

class Process(BaseModel):
    id: str
    status: str
    created_at: Optional[datetime] = None
    number_of_files: Optional[int] = 0
    completed_at: Optional[datetime] = None


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
    cur.executescript('''
        CREATE TABLE IF NOT EXISTS process (
            id TEXT PRIMARY KEY,
            status TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            number_of_files INTEGER,
            completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS result (
            id TEXT PRIMARY KEY,
            process_id TEXT NOT NULL,
            file_name TEXT NOT NULL,
            total_words INTEGER,
            total_lines INTEGER,
            total_chars INTEGER,
            most_frequent_words INTEGER,
            summary TEXT,
            FOREIGN KEY (process_id) REFERENCES process(id)
        );
    ''')

    conn.commit()
    conn.close()


def create_process(process_id, number_files):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(f"INSERT INTO process (id, status, number_of_files) VALUES (?, ?, ?)", (process_id, EnumStatus.PENDING.value, number_files))
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


def status_completed(process_id):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(f"UPDATE process SET status = '{EnumStatus.COMPLETED.value}', completed_at = {datetime.utcnow()} WHERE id = ?", (process_id,))
    conn.commit()
    conn.close()


def write_result(result: Result):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        f"INSERT INTO result (id, process_id, file_name, total_words, total_chars, total_lines, summary, most_frequent_words) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (result.id, result.process_id, result.file_name, result.total_words, result.total_chars, result.total_lines,
         result.summary, result.most_frequent_words))
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

def get_results(process_id):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute(f"SELECT process.*, result.file_name, result.total_words, result.total_lines, result.total_chars, result.most_frequent_words, result.summary FROM process JOIN result ON process.id = result.process_id WHERE process.id =? ;", (process_id,))
    rows = cur.fetchall()
    rows = [dict(row) for row in rows]
    conn.close()

    process = get_process(process_id)
    if process:
        process = process[0]
    else:
        raise Exception("Related process not found")
    return mapping_results(rows, process)

def mapping(rows):
    if rows:
        return [Process(id=x[0], status=x[1], created_at=x[2], number_of_files=x[3], completed_at=x[4]) for x in rows]
    return []


def _merge_frequent_words(merged: dict, words: dict):
    print("merged: ", merged)
    words = {x:v+merged[x] if x in merged else v for x,v in words.items()}
    merged.update(words)
    return dict(sorted(merged.items(), key=lambda item: item[1], reverse=True))


def mapping_results(results, process):
    out_result = ResultOut()
    out_result.progress.processed_files = len(results)
    out_result.progress.total_files = process.number_of_files
    out_result.progress.percentage = len(results) / process.number_of_files

    if process.completed_at:
        out_result.estimated_completion = process.completed_at
    else:
        time_taken_until = (datetime.utcnow().timestamp() - process.created_at.timestamp())\
                           / out_result.progress.percentage
        out_result.estimated_completion = process.created_at + timedelta(seconds=time_taken_until)

    out_result.status = process.status
    out_result.process_id = process.id
    out_result.started_at = process.created_at

    for r in results:
        out_result.results.total_lines+=r["total_lines"]
        out_result.results.total_chars+=r["total_chars"]
        out_result.results.total_words+=r["total_words"]
        out_result.results.files_processed.append(r["file_name"])
        out_result.results.files_summary.append(r["summary"])
        out_result.results.most_frequent_words = _merge_frequent_words(out_result.results.most_frequent_words,
                                                                      json.loads(r["most_frequent_words"]))
    return out_result.dict()