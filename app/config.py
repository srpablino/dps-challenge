from dotenv import load_dotenv
import os
import json
load_dotenv()

OPEN_AI_KEY = os.environ.get("OPEN_AI_KEY","")
TOP_NUMBER_FREQUENT_WORDS = int(os.environ.get("TOP_NUMBER_FREQUENT_WORDS","0"))
STOP_WORDS = json.loads(os.environ.get("STOP_WORDS","[]"))
