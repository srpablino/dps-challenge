import logging
from pathlib import Path

from dotenv import load_dotenv
import os
import json
from app.shared.logger import setup_logging_json

# sqlite db storage path
DB_PATH = Path("tasks/data.db")
# files storage path
TRIGGER_DIR = Path("tasks/incoming")
# create these directories if dont exist
TRIGGER_DIR.mkdir(parents=True, exist_ok=True)


def get_logger(name):
    setup_logging_json(name)
    return logging.getLogger(name)

# read optional env variables
load_dotenv()
OPEN_AI_KEY = os.environ.get("OPEN_AI_KEY","")
TOP_NUMBER_FREQUENT_WORDS = int(os.environ.get("TOP_NUMBER_FREQUENT_WORDS","0"))
STOP_WORDS = json.loads(os.environ.get("STOP_WORDS","[]"))
