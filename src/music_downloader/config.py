# config file, create config at .config/soundpp-dl/config.json
from pathlib import Path

def check_config():
    config_dir = Path('~/.config/soundpp-dl/').expanduser()
    config_file = config_dir / "config.json"

    config_dir.mkdir(parents=True, exist_ok=True)
    config_file.touch(exist_ok=True)
