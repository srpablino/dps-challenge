from config import get_logger
import uvicorn

_logger = get_logger("API")
uvicorn.run("api:app", host="0.0.0.0", port=8000, log_level="info")
