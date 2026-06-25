from __future__ import annotations

import base64
import binascii
import re
from typing import Mapping

DATA_URL_RE = re.compile(r"^data:image/(png|webp|jpeg|jpg);base64,(?P<data>[A-Za-z0-9+/=\n\r]+)$")
SAFE_ASSET_NAME_RE = re.compile(r"^[A-Za-z0-9._@+-]+\.png$")
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
MAX_SINGLE_ASSET_BYTES = 8 * 1024 * 1024


def decode_asset_data(asset_data: Mapping[str, str] | None) -> dict[str, bytes]:
    """Decode an {filename: dataURL} payload from the web UI.

    Only safe PNG file names are accepted. JPEG/WebP data URLs are allowed only
    if the browser has already converted them into PNG before upload; the server
    rejects non-PNG bytes to keep the export deterministic.
    """
    result: dict[str, bytes] = {}
    if not asset_data:
        return result
    for filename, data_url in asset_data.items():
        if not isinstance(filename, str) or not SAFE_ASSET_NAME_RE.match(filename):
            raise ValueError(f"Unsafe asset filename: {filename!r}")
        if not isinstance(data_url, str):
            raise ValueError(f"Asset {filename} must be a data URL string")
        match = DATA_URL_RE.match(data_url)
        if not match:
            raise ValueError(f"Asset {filename} is not a supported data URL")
        try:
            raw = base64.b64decode(match.group("data"), validate=True)
        except binascii.Error as exc:
            raise ValueError(f"Asset {filename} contains invalid base64") from exc
        if len(raw) > MAX_SINGLE_ASSET_BYTES:
            raise ValueError(f"Asset {filename} is too large")
        if not raw.startswith(PNG_MAGIC):
            raise ValueError(f"Asset {filename} must be PNG after browser conversion")
        result[filename] = raw
    return result
