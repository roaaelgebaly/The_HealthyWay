import os
from dotenv import load_dotenv
load_dotenv()  

def get_secret(name: str, default: str | None = None) -> str | None:
    return os.environ.get(name, default)

LLM_MODEL = get_secret("LLM_MODEL", "openai/gpt-oss-120b")