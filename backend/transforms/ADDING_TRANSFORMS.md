# Ajouter un nouveau Transform (plugin)

> **Production** : les transforms actifs sont des **plugins** dans `backend/plugins/<id>/` (`plugin.json` + `plugin.py`).  
> Le dossier `backend/transforms/` est legacy (tests uniquement). Référence : plugin `death_search`.

## Structure plugin (recommandé)

```
backend/plugins/mon_plugin/
  plugin.json    # manifest (input_types, output_types, …)
  plugin.py      # class MonPlugin(TransformPlugin)
```

Exemple de manifest :

```json
{
  "id": "mon_plugin",
  "name": "Mon Plugin",
  "category": "Network",
  "description": "Ce que ça fait",
  "input_types": ["DOMAIN"],
  "output_types": ["IP"],
  "entrypoint": "plugin.py"
}
```

## Pattern minimal (`plugin.py`)

```python
from plugins.base import PluginContext, TransformPlugin
from plugins.helpers import build_observation

class MonPlugin(TransformPlugin):
    async def run(self, context: PluginContext) -> dict:
        value = context.entity.label.strip()
        log = [f"[MonPlugin] Starting…"]
        nodes, edges, observations = [], [], []

        # --- logique ---
        nodes.append({
            "type": "IP",
            "label": "1.2.3.4",
            "properties": {"source": "mon_plugin"},
        })
        observations.append(build_observation(
            "mon_plugin",
            {"field": "ip", "value": "1.2.3.4"},
            collection_method="PUBLIC_SEARCH",
            confidence=0.7,
            status="UNVERIFIED",
        ))
        log.append("[MonPlugin] Done")

        return {"nodes": nodes, "edges": edges, "observations": observations, "log": log}
```

Enregistrement : automatique via `PluginRegistry` au démarrage. Ajouter l'id dans `backend/tests/test_plugins.py` (`EXPECTED_PLUGINS`).

---

## Legacy (`backend/transforms/` — ne pas étendre)

```python
# backend/transforms/mon_outil.py — OBSOLÈTE pour l'API /transforms
from transforms.base import Transform, register

@register
class MonOutil(Transform):
    ...
```

---

## Traductions i18n

Dans `frontend/src/i18n/locales/en.ts` et `fr.ts`, bloc `transforms.catalog` :

```ts
mon_plugin: { display_name: 'My Plugin', description: 'What it does' },
```

Optionnel : `TransformPanel.tsx` → `TRANSFORM_EDGE_TYPE.mon_plugin`.

---

## Exemples de plugins existants

| Plugin | Input | Fournisseur |
|--------|-------|-------------|
| `dns_lookup` | DOMAIN | - |
| `sherlock_lookup` | USERNAME | sherlock-project |
| `maigret_lookup` | USERNAME | maigret |
| `spiderfoot_scan` | PERSON, DOMAIN, … | SpiderFoot |
| `death_search` | PERSON | INSEE / data.gouv.fr — voir [`docs/DEATH_SEARCH.md`](../../docs/DEATH_SEARCH.md) |

---

## Librairies avec API key (`.env`)

```
SHODAN_API_KEY=xxx
HIBP_API_KEY=xxx
DEATH_RECORDS_PATH=/chemin/vers/parts
```

Puis dans le plugin : `os.getenv("SHODAN_API_KEY")` ou `context.config`.

---

## Tests

```bash
cd backend && PYTHONPATH=. pytest tests/test_plugins.py tests/test_<plugin>.py -q
```
