# config file, create config at .config/soundpp-dl/config.json
from pathlib import Path
import json

CONFIG_DIR = Path('~/.config/soundpp-dl/').expanduser()
CONFIG_FILE = CONFIG_DIR / "config.json"

DEFAULT_CONFIG = {
    "output_dir": str(Path.home() / "Music")
}

def check_config_file():
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)

    if not CONFIG_FILE.exists() or CONFIG_FILE.stat().st_size == 0:
        jsonobj = json.dumps(DEFAULT_CONFIG, indent=2)
        CONFIG_FILE.write_text(jsonobj)

    json.loads(CONFIG_FILE.read_text())
    return
