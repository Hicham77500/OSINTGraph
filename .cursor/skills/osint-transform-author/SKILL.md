---
name: osint-transform-author
description: Author OSINT transform plugins for OSINTGraph backend with mandatory provenance in return payload. Use when adding or modifying transforms in backend/transforms/.
---

# OSINT Transform Author

## When to use

Adding or modifying a transform in `backend/transforms/`.

## Reference

Read `backend/transforms/ADDING_TRANSFORMS.md` and `backend/transforms/base.py`.

## Steps

1. Create `backend/transforms/my_transform.py`
2. Subclass `Transform`, set `name`, `display_name`, `input_type`, `output_type`, `description`
3. Decorate with `@register`
4. Implement `async def run(self, value, options) -> dict`

## Required return shape

```python
{
    "nodes": [{"type": str, "label": str, "properties": dict}],
    "edges": [],
    "observations": [{
        "source": {
            "platform": "dns",  # or shodan, manual, etc.
            "collection_method": "TRANSFORM",  # MANUAL|PUBLIC_SEARCH|OFFICIAL_API|IMPORT|TRANSFORM
            "url": None,
        },
        "content": {"field": "ip", "value": "1.2.3.4"},
        "confidence": 0.9,
        "status": "UNVERIFIED",
    }],
    "log": ["[MY_TRANSFORM] Step without PII"],
}
```

## Rules

- Catch errors internally; append to `log`, do not leak stack traces with user input
- Never log emails, phones, or tokens in `log`
- Use `asyncio.to_thread` for sync libraries
- Add i18n entries in `frontend/src/i18n/locales/en.ts` and `fr.ts` under `transforms.catalog`
- Do not return fake data when API key missing — return empty nodes + clear log message
- Register compatible `input_type` with existing NodeType union or extend via domain entity types

## Test

Add pytest in `backend/tests/test_transforms.py` asserting registry includes new transform.
