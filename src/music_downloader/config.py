# config file, create config at .config/soundpp-dl/config.json
from pathlib import Path
import json

CONFIG_DIR = Path('~/.config/soundpp-dl/').expanduser()
CONFIG_FILE = CONFIG_DIR / "config.json"

DEFAULT_CONFIG = {
    "output_dir": str(Path.home() / "Music")
}

def load_config() -> dict:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)

    if not CONFIG_FILE.exists() or CONFIG_FILE.stat().st_size == 0:
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG.copy()

    try:
        user_config = json.loads(CONFIG_FILE.read_text())
        if not isinstance(user_config, dict):
            raise ValueError("Config root is a not JSON object")
    except (json.JSONDecodeError, ValueError):
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG.copy()

    config = DEFAULT_CONFIG | user_config

    if not isinstance(config.get("output_dir"), str) or not config["output_dir"].strip():
        config["output_dir"] = DEFAULT_CONFIG["output_dir"]

    if config != user_config:
        save_config(config)

    return config


def save_config(config: dict) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(json.dumps(config, indent=4))
