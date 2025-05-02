import json
from pathlib import Path
from pydantic import BaseModel, FIeld

class AppConfig(BaseModel):
    show_shorts: bool

def load_config() -> AppConfig:
    cfg_file = Path(__file__).parent / "config.json"
    data = json.loads(cfg_file.read_text())
    return AppConfig(**data)