import re
import time
import json
import logging
import requests
from urllib.parse import quote

logger = logging.getLogger("diskwala_bot")

API_DOWNLOAD = "https://api2.diskwala.net/api/diskwala/download/d"
API_STATUS = "https://api2.diskwala.net/api/diskwala/status"
ENCRYPTION_KEY = "e7109544dab612bd5b80b8a427ac474ba5541b9efff7a4ca1c8ef85df2489c23"


def _get_endpoints(link: str) -> tuple[str, str]:
    """Return (download_api, status_api) based on which service the link belongs to."""
    if "flezen.com" in link.lower():
        return (
            "https://api2.diskwala.net/api/flezen/download",
            "https://api2.diskwala.net/api/flezen/status?link=",
        )
    return (
        API_DOWNLOAD,
        API_STATUS + "?link=",
    )


def decrypt_file(file_data: dict) -> dict:
    """Decrypt AES-GCM encrypted file response from Diskwala API."""
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM

    key = bytes.fromhex(ENCRYPTION_KEY)
    iv = bytes.fromhex(file_data["s"])
    ciphertext = bytes.fromhex(file_data["p"] + file_data["h"])

    aesgcm = AESGCM(key)
    plaintext = aesgcm.decrypt(iv, ciphertext, None)
    return json.loads(plaintext.decode("utf-8"))


def extract_diskwala_links(text: str) -> list[str]:
    """Extract Diskwala/Flezen URLs from text."""
    patterns = [
        r"https?://(?:www\.)?diskwala\.com/app/[A-Za-z0-9]+",
        r"https?://(?:www\.)?diskwala\.com/playlist/[A-Za-z0-9]+",
        r"https?://(?:www\.)?flezen\.com/[A-Za-z0-9]+",
    ]
    links = []
    for pattern in patterns:
        links.extend(re.findall(pattern, text))
    return list(dict.fromkeys(links))


def fetch_diskwala_video(link: str, auth: str) -> dict:
    """Fetch video info from Diskwala API."""
    headers = {
        "Authorization": f"Bearer {auth}",
        "X-Bot-Id": "diskwala",
        "Content-Type": "application/json",
        "Origin": "https://miniapp.diskwala.net",
        "Referer": "https://miniapp.diskwala.net/",
        "User-Agent": "Mozilla/5.0 (Linux; Android 13) AppleWebKit/537.36",
    }

    download_api, status_api_prefix = _get_endpoints(link)

    logger.info(f"Calling API: {download_api}")

    r = requests.post(download_api, headers=headers, json={"link": link}, timeout=60)
    logger.info(f"Download response: {r.status_code} - {r.text[:200]}")
    data = r.json()

    if not data.get("ok"):
        raise Exception(data.get("error", f"API Error: {data}"))

    status_url = status_api_prefix + quote(link, safe="")

    for _ in range(90):
        r = requests.get(status_url, headers=headers, timeout=60)
        data = r.json()

        if not data.get("ok"):
            raise Exception(data.get("error", f"API Error: {data}"))

        status = data.get("status", "").lower()

        if status == "pending":
            time.sleep(2)
            continue

        if status == "done":
            file = data.get("file")
            if not file:
                raise Exception(f"No file returned: {data}")

            # Decrypt if encrypted
            if file.get("_x"):
                logger.info("File is encrypted, decrypting...")
                file = decrypt_file(file)
                logger.info(f"Decrypted file: {json.dumps(file)[:300]}")

            def _pick(d, *keys):
                for k in keys:
                    if k in d and d[k] not in (None, ""):
                        return d[k]
                return None

            return {
                "name": _pick(file, "name", "fileName", "filename", "title") or "video.mp4",
                "size": _pick(file, "size", "fileSize", "length") or 0,
                "downloadUrl": _pick(file, "downloadUrl", "download_url", "url", "link"),
                "streamUrl": _pick(file, "streamUrl", "stream_url", "hls") or _pick(file, "downloadUrl", "download_url", "url", "link"),
                "thumb": file.get("thumb"),
            }

        raise Exception(f"Unexpected status: {status} - {data}")

    raise Exception("Timeout waiting for Diskwala API response")
