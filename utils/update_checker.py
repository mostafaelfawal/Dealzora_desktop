import requests
import json
import base64
import os
from dotenv import load_dotenv
from packaging import version

# تحميل .env
load_dotenv()

OWNER = "mostafaelfawal"
REPO = "Dealzora_desktop"
FILE_PATH = "version.json"

APP_VERSION = "1.4.5"


def check_for_update():
    try:
        url = f"https://api.github.com/repos/{OWNER}/{REPO}/contents/{FILE_PATH}"

        token = os.getenv("GITHUB_TOKEN")

        headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "Dealzora-App"
        }

        # ضيف التوكن لو موجود
        if token:
            headers["Authorization"] = f"token {token}"

        r = requests.get(url, timeout=5, headers=headers)
        r.raise_for_status()

        data = r.json()

        content = base64.b64decode(data["content"]).decode("utf-8")
        json_data = json.loads(content)

        latest_version = json_data.get("version")
        download_url = json_data.get("url")

        if latest_version and version.parse(latest_version) > version.parse(APP_VERSION):
            return latest_version, download_url

        return None, None

    except Exception as e:
        print("Update check failed:", e)
        return None, None