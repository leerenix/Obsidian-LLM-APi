import os
from dotenv import load_dotenv

load_dotenv()

OBSIDIAN_API_URL = os.getenv("OBSIDIAN_API_URL")
OBSIDIAN_API_KEY = os.getenv("OBSIDIAN_API_KEY")
LLM_API_URL = os.getenv("LLM_API_URL")
LLM_API_KEY = os.getenv("LLM_API_KEY")
LLM_MODEL_NAME = os.getenv("LLM_MODEL_NAME")
