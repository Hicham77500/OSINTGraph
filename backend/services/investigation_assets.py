"""Store investigation images for visual search (analyst uploads only)."""
from __future__ import annotations

import hashlib
import os
import re
import uuid
from pathlib import Path

ALLOWED_MIME = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
    "image/gif": ".gif",
}
MAX_BYTES = 8 * 1024 * 1024


def assets_dir() -> Path:
    base = os.getenv("INVESTIGATION_ASSETS_PATH")
    if base:
        path = Path(base)
    else:
        db = Path(os.getenv("SQLITE_PATH", "osintgraph.db"))
        path = db.parent / "investigation_assets"
    path.mkdir(parents=True, exist_ok=True)
    return path


def _safe_filename(name: str) -> str:
    base = Path(name).name
    return re.sub(r"[^a-zA-Z0-9._-]", "_", base)[:120] or "upload.jpg"


def save_image(content: bytes, filename: str, content_type: str) -> dict[str, str]:
    if content_type not in ALLOWED_MIME:
        raise ValueError(f"Unsupported image type: {content_type}")
    if len(content) > MAX_BYTES:
        raise ValueError("Image exceeds 8 MB limit")

    asset_id = uuid.uuid4().hex
    ext = ALLOWED_MIME[content_type]
    safe = _safe_filename(filename)
    if not safe.lower().endswith(ext):
        safe = f"{Path(safe).stem}{ext}"

    dest = assets_dir() / f"{asset_id}{ext}"
    dest.write_bytes(content)
    sha256 = hashlib.sha256(content).hexdigest()

    return {
        "asset_id": asset_id,
        "filename": safe,
        "content_type": content_type,
        "sha256": sha256,
        "storage_name": dest.name,
    }


def get_asset_path(asset_id: str) -> Path | None:
    if not re.fullmatch(r"[a-f0-9]{32}", asset_id):
        return None
    folder = assets_dir()
    for path in folder.glob(f"{asset_id}.*"):
        if path.is_file():
            return path
    return None
