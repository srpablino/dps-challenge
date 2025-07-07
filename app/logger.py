import json
import logging
import sys

class JsonFormatter(logging.Formatter):
    def __init__(self, name):
        super().__init__()
        self.name = name

    def format(self, record):
        log_record = {
            "time": self.formatTime(record),
            "level": record.levelname,
            "name": self.name,
            "message": record.getMessage(),
        }
        return json.dumps(log_record)


def setup_logging_json(name):

    root_logger = logging.getLogger(name)
    root_logger.setLevel(logging.INFO)
    root_logger.propagate = False

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter(name))
    root_logger.addHandler(handler)

    file_handler = logging.FileHandler(f"tasks/{name}.log")
    file_handler.setFormatter(JsonFormatter(name))
    root_logger.addHandler(file_handler)

    for uvicorn_logger_name in ("uvicorn", "uvicorn.error", "uvicorn.access"):
        logger = logging.getLogger(uvicorn_logger_name)
        logger.setLevel(logging.INFO)
        logger.handlers.clear()
        logger.propagate = False
        logger.handlers.append(handler)
        logger.handlers.append(file_handler)
