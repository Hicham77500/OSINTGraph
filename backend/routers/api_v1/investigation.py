"""Visual investigation uploads and search assistant links."""
from __future__ import annotations

import os

from fastapi import APIRouter, File, HTTPException, Query, Request, UploadFile
from fastapi.responses import FileResponse

from services.investigation_assets import get_asset_path, save_image
from services.visual_search import build_search_assistants
from services.general_search import (
    build_forum_keyword_links,
    build_person_name_links,
    build_phone_public_links,
    build_social_platform_links,
    build_vehicle_plate_links,
    build_web_browser_links,
)

router = APIRouter(prefix="/investigation", tags=["investigation"])


def _public_asset_url(request: Request, asset_id: str) -> str:
    base = str(request.base_url).rstrip("/")
    return f"{base}/api/v1/investigation/assets/{asset_id}"


@router.post("/visual-search/upload")
async def upload_visual_search_image(
    request: Request,
    file: UploadFile = File(...),
    linked_person: str | None = Query(None),
    linked_place: str | None = Query(None),
):
    """Upload an image for reverse-search assistants (no automated scraping)."""
    if not file.content_type:
        raise HTTPException(400, "Missing content type")
    raw = await file.read()
    try:
        meta = save_image(raw, file.filename or "upload.jpg", file.content_type)
    except ValueError as e:
        raise HTTPException(400, str(e)) from e

    public_url = _public_asset_url(request, meta["asset_id"])
    assistants = build_search_assistants(public_url)

    return {
        "ok": True,
        **meta,
        "public_url": public_url,
        "linked_person": linked_person,
        "linked_place": linked_place,
        "assistants": assistants,
        "disclaimer": "Links open official search UIs. Results are not imported automatically — document findings with provenance.",
    }


@router.get("/visual-search/assistants")
async def list_visual_search_assistants(request: Request, asset_id: str | None = None):
    public_url = _public_asset_url(request, asset_id) if asset_id else None
    return {"assistants": build_search_assistants(public_url)}


@router.get("/general-search")
async def general_search_assistants(
    q: str,
    mode: str = "web",
    keywords: str | None = Query(None, description="Comma-separated forum keywords"),
    country: str = Query("FR"),
    fetch: bool = Query(False, description="When true, return result_cards with real hits"),
):
    """Public search-engine / social / forum link bundles (no automated scraping)."""
    if not q.strip():
        raise HTTPException(400, "Query q is required")
    q = q.strip()
    kw = [k.strip() for k in (keywords or "").split(",") if k.strip()]

    if mode == "social":
        items = build_social_platform_links(q)
    elif mode == "forum":
        items = build_forum_keyword_links(q, kw or None)
    elif mode == "phone":
        items = build_phone_public_links(q)
    elif mode == "plate":
        items = build_vehicle_plate_links(q, country=country)
    elif mode == "person":
        parts = q.split()
        first = parts[0] if parts else None
        last = parts[-1] if len(parts) > 1 else None
        items = build_person_name_links(first, last, q)
    else:
        items = build_web_browser_links(q)

    result_cards: list[dict] = []
    if fetch:
        brave = os.getenv("BRAVE_SEARCH_API_KEY")
        if mode == "forum":
            from services.web_search_results import fetch_site_findings
            for kw in (kw or ["reddit"])[:4]:
                result_cards.extend(await fetch_site_findings("reddit.com", f"{q} {kw}", brave))
        elif mode == "social":
            from services.web_search_results import fetch_site_findings
            for site in ("facebook.com", "linkedin.com", "instagram.com"):
                result_cards.extend(await fetch_site_findings(site, q, brave))
        else:
            result_cards = await fetch_web_findings(q, brave_api_key=brave)

    return {
        "query": q,
        "mode": mode,
        "assistants": items,
        "result_cards": result_cards[:12],
        "disclaimer": "Public search links only. Verify findings and record provenance. No harassment or private-data bypass.",
    }


@router.get("/assets/{asset_id}")
async def serve_investigation_asset(asset_id: str):
    path = get_asset_path(asset_id)
    if not path:
        raise HTTPException(404, "Asset not found")
    media = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".webp": "image/webp",
        ".gif": "image/gif",
    }.get(path.suffix.lower(), "application/octet-stream")
    return FileResponse(path, media_type=media, filename=path.name)
