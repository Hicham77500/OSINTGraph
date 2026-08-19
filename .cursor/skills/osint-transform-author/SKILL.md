---
name: osint-transform-author
description: Author OSINT transform plugins for OSINTGraph backend with mandatory provenance in return payload. Use when adding or modifying transforms in backend/plugins/.
---

# OSINT Transform Author

## When to use

Adding or modifying a transform plugin in `backend/plugins/`.

## Reference

- `backend/plugins/base.py` — `TransformPlugin`, `PluginContext`
- `backend/plugins/death_search/` — example with DuckDB + observations
- `backend/transforms/ADDING_TRANSFORMS.md` — guide (plugins = production)
- `docs/DEATH_SEARCH.md` — death records plugin specifics

## Steps

1. Create `backend/plugins/my_plugin/plugin.json`
2. Create `backend/plugins/my_plugin/plugin.py`
3. Subclass `TransformPlugin`, implement `async def run(self, context: PluginContext) -> dict`
4. Add plugin id to `backend/tests/test_plugins.py` (`EXPECTED_PLUGINS`)
5. Add i18n under `transforms.catalog.my_plugin` in `en.ts` / `fr.ts`

## Required return shape

```python
{
    "nodes": [{"type": str, "label": str, "properties": dict}],
    "edges": [],
    "observations": [{
        "source": {
            "platform": str,
            "collection_method": "MANUAL|PUBLIC_SEARCH|OFFICIAL_API|IMPORT|TRANSFORM",
            "url": str | None,
        },
        "content": dict,
        "confidence": float,
        "status": "UNVERIFIED",
    }],
    "log": ["[MY_PLUGIN] Step without PII"],
}
```

## Rules

- Catch errors internally; append to `log`, do not leak stack traces with user input
- Never log emails, phones, names, or tokens in `log`
- Use `asyncio.to_thread` for sync OSINT libs (DuckDB, subprocess, etc.)
- Do not return fake data when config missing — empty nodes + clear log message
- Register compatible `input_types` with domain entity types in manifest

## Test

Add pytest in `backend/tests/` for plugin logic; ensure `test_plugins.py` includes the new id.
