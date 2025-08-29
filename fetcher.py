"""
fetcher.py
Network-related helpers: fetching record metadata and cover images.
"""
from typing import Optional
from io import BytesIO

import requests
from PIL import Image

import config
from model import Record


def fetch_cover(url: str) -> Optional[Image.Image]:
    """Fetch an image from `url` returning an RGB PIL Image or None on failure."""
    try:
        resp = requests.get(url, timeout=5)
        resp.raise_for_status()
        return Image.open(BytesIO(resp.content)).convert("RGB")
    except Exception:
        return None


def fetch_record(input_str: str) -> Optional[Record]:
    """
    Given a short code (6 chars) or a full URL, fetch the record metadata and cover.
    Returns a Record instance or None on failure.
    """
    try:
        if len(input_str) == 6:
            resp = requests.get(f"{config.HOST_URL}/plays/scan/{input_str}", timeout=5)
        else:
            resp = requests.get(input_str, timeout=5)
        resp.raise_for_status()
        data = resp.json().get("record", {}) or {}
        if not data:
            return None

        title = data.get("title", "Unknown Album")
        artists = data.get("artists", "Unknown Artist")
        section = data.get("section", "N/A")
        code = data.get("code", "XXXXXX")
        cover_path = data.get("cover_path")
        cover_img = fetch_cover(f"{config.HOST_URL}{cover_path}") if cover_path else None

        return Record(title=title, artists=artists, section=section, code=code, cover_path=cover_path, cover_img=cover_img)
    except Exception:
        return None
