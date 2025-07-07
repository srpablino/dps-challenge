import logging
from pathlib import Path

from dotenv import load_dotenv
import os
import json
from app.shared.logger import setup_logging_json

DB_PATH = Path("tasks/data.db")
TRIGGER_DIR = Path("tasks/incoming")
TRIGGER_DIR.mkdir(parents=True, exist_ok=True)


def get_logger(name):
    setup_logging_json(name)
    return logging.getLogger(name)


load_dotenv()
OPEN_AI_KEY = os.environ.get("OPEN_AI_KEY","")
TOP_NUMBER_FREQUENT_WORDS = int(os.environ.get("TOP_NUMBER_FREQUENT_WORDS","0"))
STOP_WORDS = json.loads(os.environ.get("STOP_WORDS","[]"))
