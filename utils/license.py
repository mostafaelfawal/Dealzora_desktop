import hashlib
import winreg
import socket
from pathlib import Path

SECRET_KEY = "mostafa-hamdi-dealzora"

LICENSE_FILE = Path.home() / ".dealzora_license"

def get_machine_guid():
    try:
        key = winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Cryptography"
        )
        guid, _ = winreg.QueryValueEx(key, "MachineGuid")
        return guid
    except Exception:
        try:
            return socket.gethostname()
        except:
            return "UNKNOWN_MACHINE"


def generate_expected_license():
    guid = get_machine_guid()
    if not guid:
        return None

    raw = f"{guid}-{SECRET_KEY}"
    return hashlib.sha256(raw.encode()).hexdigest()


def is_license_valid():
    if not LICENSE_FILE.exists():
        return False

    saved_license = LICENSE_FILE.read_text().strip()
    return saved_license == generate_expected_license()


def save_license(license_key: str):
    LICENSE_FILE.write_text(license_key)
