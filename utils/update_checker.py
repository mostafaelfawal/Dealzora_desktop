import requests
from json import loads

def get_current_version():
    try:
        with open("version.json", "r") as f:
            data = f.read()
            version_info = loads(data)
            return version_info.get("version", "1.0.0")
    except:
        return "1.0.0"
    
def check_for_update():
    try:
        r = requests.get(VERSION_URL, timeout=5)
        data = r.json()

        latest_version = data["version"]
        download_url = data["url"]

        if latest_version != APP_VERSION:
            return latest_version, download_url

        return None, None

    except:
        return None, None

VERSION_URL = "https://raw.githubusercontent.com/USERNAME/REPO/main/version.json"
APP_VERSION = get_current_version()


