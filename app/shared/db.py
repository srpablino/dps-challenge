import sqlite3
from datetime import datetime
from app.shared.mapper import mapping, mapping_results
from app.shared.models import EnumStatus, Result
from app.shared.config import get_logger, DB_PATH

_logger = get_logger("DB")


def init_db():
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.executescript('''
            CREATE TABLE IF NOT EXISTS process (
                id TEXT PRIMARY KEY,
                status TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                number_of_files INTEGER,
                completed_at TIMESTAMP DEFAULT NULL
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
    except Exception as ex:
        _logger.error(f"Error creating db - {ex}")
        raise Exception("DB could not be created")


def create_process(process_id, number_files):
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute(f"INSERT INTO process (id, status, number_of_files) VALUES (?, ?, ?)", (process_id, EnumStatus.PENDING.value, number_files))
        conn.commit()
        conn.close()
    except Exception as ex:
        _logger.error(f"Error creating process {process_id} in db - {ex}")
        raise


def get_pending_processes():
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute(f"SELECT * FROM process WHERE status = ?", (EnumStatus.PENDING.value,))
        rows = cur.fetchall()
        conn.close()
        return mapping(rows)
    except Exception as ex:
        _logger.error(f"Error getting pending processes - {ex}")
        raise

def status_update(process_id, status):
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute(f"UPDATE process SET status = ? WHERE id = ?", (status, process_id,))
        conn.commit()
        conn.close()
    except Exception as ex:
        _logger.error(f"Error updating {process_id} to status {status} in db - {ex}")
        raise


def status_completed(process_id):
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute(f"UPDATE process SET status = ?, completed_at = ? WHERE id = ?", (EnumStatus.COMPLETED.value, datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'), process_id,))
        conn.commit()
        conn.close()
    except Exception as ex:
        _logger.error(f"Error updating process {process_id} to complete in db - {ex}")
        raise


def write_result(result: Result):
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute(
            f"INSERT INTO result (id, process_id, file_name, total_words, total_chars, total_lines, summary, most_frequent_words) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (result.id, result.process_id, result.file_name, result.total_words, result.total_chars, result.total_lines,
             result.summary, result.most_frequent_words))
        conn.commit()
        conn.close()
    except Exception as ex:
        _logger.error(f"Error writing file result {result.file_name} for process {result.process_id} in db - {ex}")
        raise


def get_process(process_id):
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute(f"SELECT * FROM process where id = ?", (process_id,))
        rows = cur.fetchall()
        conn.close()
        return mapping(rows)
    except Exception as ex:
        _logger.error(f"Error getting process {process_id} from db - {ex}")
        raise


def get_process_list():
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute(f"SELECT * FROM process")
        rows = cur.fetchall()
        conn.close()
        return mapping(rows)
    except Exception as ex:
        _logger.error(f"Error getting process list from db - {ex}")
        raise

def get_results(process_id):
    try:
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
    except Exception as ex:
        _logger.error(f"Error getting results for {process_id} from db - {ex}")
        raise
