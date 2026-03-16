import requests

VERSION_URL = "https://raw.githubusercontent.com/mostafaelfawal/Dealzora_desktop/main/version.json"
APP_VERSION = "1.1.0"


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
