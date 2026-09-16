"""Public reverse-image search assistants — links only, no scraped results."""
from __future__ import annotations

from urllib.parse import quote


def build_search_assistants(public_image_url: str | None) -> list[dict[str, str]]:
    """
    Return analyst-facing links to official search UIs.
    Google/Bing/Yandex URL search requires a publicly reachable image URL.
    """
    assistants: list[dict[str, str]] = [
        {
            "id": "google_lens",
            "name": "Google Lens",
            "url": "https://lens.google.com/",
            "method": "MANUAL",
            "hint": "Upload the image manually (Lens does not allow embedding).",
        },
        {
            "id": "google_images",
            "name": "Google Images",
            "url": "https://images.google.com/",
            "method": "MANUAL",
            "hint": "Use Search by image after upload, or URL if your image is public.",
        },
        {
            "id": "bing_visual",
            "name": "Bing Visual Search",
            "url": "https://www.bing.com/visualsearch",
            "method": "MANUAL",
            "hint": "Paste image or drag file into Bing Visual Search.",
        },
        {
            "id": "yandex",
            "name": "Yandex Images",
            "url": "https://yandex.com/images/",
            "method": "MANUAL",
            "hint": "Use the camera icon to search by image.",
        },
        {
            "id": "tineye",
            "name": "TinEye",
            "url": "https://tineye.com/",
            "method": "MANUAL",
            "hint": "Upload copy saved from this investigation workspace.",
        },
    ]

    if public_image_url:
        encoded = quote(public_image_url, safe="")
        assistants.append({
            "id": "google_by_url",
            "name": "Google (image URL)",
            "url": f"https://www.google.com/searchbyimage?image_url={encoded}",
            "method": "PUBLIC_SEARCH",
            "hint": "Works only if the image URL is reachable from the public internet.",
        })
        assistants.append({
            "id": "bing_by_url",
            "name": "Bing (image URL)",
            "url": (
                "https://www.bing.com/images/search"
                f"?view=detailv2&iss=sbi&form=SBIIDP&sbisrc=UrlPaste&q=imgurl:{encoded}"
            ),
            "method": "PUBLIC_SEARCH",
            "hint": "Requires a public HTTPS URL to your uploaded asset.",
        })
        assistants.append({
            "id": "yandex_by_url",
            "name": "Yandex (image URL)",
            "url": f"https://yandex.com/images/search?rpt=imageview&url={encoded}",
            "method": "PUBLIC_SEARCH",
            "hint": "Requires a public HTTPS URL to your uploaded asset.",
        })

    return assistants
