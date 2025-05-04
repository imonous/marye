import json
from pathlib import Path
from pydantic import BaseModel, Field

CFG_PATH = Path(__file__).parent.parent / "config.json"

class AppConfig(BaseModel):
    show_shorts: bool

def load_config() -> AppConfig:
    data = json.loads(CFG_PATH.read_text())
    return AppConfig(**data)