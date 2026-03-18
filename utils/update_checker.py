import requests

VERSION_URL = f"https://raw.githubusercontent.com/mostafaelfawal/Dealzora_desktop/refs/heads/main/version.json"
APP_VERSION = "1.2.2"


def check_for_update():
    try:
        r = requests.get(VERSION_URL, timeout=5, headers={"Cache-Control": "no-cache"})
        data = r.json()

        latest_version = data["version"]
        download_url = data["url"]

        if latest_version != APP_VERSION:
            return latest_version, download_url

        return None, None

    except:
        return None, None
