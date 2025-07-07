from app.shared.config import get_logger
import uvicorn

_logger = get_logger("API")
# launch FASTApi http server and link it to our API
uvicorn.run("app.api.api:app", host="0.0.0.0", port=8000, log_level="info")
