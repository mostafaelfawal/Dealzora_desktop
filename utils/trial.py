import json
import hashlib
from datetime import datetime
from pathlib import Path
from utils.license import get_machine_guid

TRIAL_FILE = Path.home() / ".dealzora_trial"
TRIAL_DAYS = 7
SECRET = "trial-mostafa-dealzora"

def _hash(data: str) -> str:
    if not data:
        return None
    return hashlib.sha256((data + SECRET).encode()).hexdigest()

def init_trial():
    if TRIAL_FILE.exists():
        return

    data = {
        "start": datetime.now().isoformat(),
        "guid": _hash(get_machine_guid())
    }
    TRIAL_FILE.write_text(json.dumps(data))

def get_remaining_days():
    if not TRIAL_FILE.exists():
        return 0

    data = json.loads(TRIAL_FILE.read_text())

    if _hash(get_machine_guid()) != data["guid"]:
        return 0  # محاولة نقل البرنامج لجهاز آخر

    start_date = datetime.fromisoformat(data["start"])
    used_days = (datetime.now() - start_date).days
    return max(0, TRIAL_DAYS - used_days)

def is_trial_valid():
    return get_remaining_days() > 0
