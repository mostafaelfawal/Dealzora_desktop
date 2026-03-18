import requests
import time

BASE_URL = "https://raw.githubusercontent.com/mostafaelfawal/Dealzora_desktop/refs/heads/main/version.json"
APP_VERSION = "1.3.4"


def check_for_update():
    try:
        # كسر الكاش بإضافة timestamp
        url = f"{BASE_URL}?t={int(time.time())}"

        r = requests.get(
            url,
            timeout=5,
            headers={
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "Pragma": "no-cache",
                "Expires": "0",
            },
        )

        r.raise_for_status()  # لو في error في الطلب

        data = r.json()

        latest_version = data.get("version")
        download_url = data.get("url")

        # مقارنة أفضل للـ versions
        if latest_version and latest_version != APP_VERSION:
            return latest_version, download_url

        return None, None

    except Exception as e:
        print("Update check failed:", e)
        return None, None
