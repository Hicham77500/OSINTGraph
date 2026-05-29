# Ajouter un nouveau Transform

## Pattern minimal (copier-coller)

```python
# backend/transforms/mon_outil.py
"""Mon Outil — Description courte"""
from transforms.base import Transform, register

@register                          # ← obligatoire : auto-découverte
class MonOutil(Transform):
    name         = "mon_outil"     # ← clé unique, snake_case
    display_name = "Mon Outil"     # ← affiché dans le panel
    input_type   = "domain"        # ← type de nœud accepté en entrée
                                   #   valeurs: person | email | domain | ip | username | organization
    output_type  = "ip"            # ← type de nœud produit en sortie
    description  = "Ce que ça fait"

    async def run(self, value: str, options: dict = {}) -> dict:
        nodes = []
        edges = []
        log   = [f"[MonOutil] Démarrage pour {value}..."]

        # --- ta logique ici ---
        nodes.append({
            "type":  "ip",               # NodeType
            "label": "1.2.3.4",          # valeur affichée sur le canvas
            "properties": {              # métadonnées libres
                "source": "mon_outil",
                "detail": "...",
            },
        })
        log.append("[MonOutil] Done — 1 résultat")
        # ----------------------

        return {"nodes": nodes, "edges": edges, "log": log}
```

Crée le fichier → sauvegarde → le backend l'auto-découvre au prochain démarrage. **Aucun autre fichier à modifier** (sauf les traductions ci-dessous).

---

## Ajouter les traductions

Dans `frontend/src/i18n/locales/en.ts` et `fr.ts`, dans le bloc `transforms.catalog` :

```ts
// en.ts
mon_outil: { display_name: 'My Tool', description: 'What it does' },

// fr.ts
mon_outil: { display_name: 'Mon Outil', description: 'Ce que ça fait' },
```

---

## Exemples de librairies OSINT à intégrer

| Librairie            | pip install              | input_type    | Ce qu'elle retourne                         |
|----------------------|--------------------------|---------------|---------------------------------------------|
| `maigret`            | `maigret`                | `username`    | Profils + infos biographiques               |
| `theHarvester`       | `theHarvester`           | `domain`      | Sous-domaines, emails, IPs, employés        |
| `ipinfo`             | `ipinfo`                 | `ip`          | Géolocalisation, ASN, organisation          |
| `phonenumbers`       | `phonenumbers`           | `username`    | Validation + portabilité d'un numéro        |
| `socialscan`         | `socialscan`             | `email`/`username` | Disponibilité sur réseaux sociaux     |
| `ghunt` (cli)        | subprocess               | `email`       | Profil Google complet                       |

---

## Librairies avec API key (à configurer dans `.env`)

```
SHODAN_API_KEY=xxx
HIBP_API_KEY=xxx
```
Puis dans ton transform : `import os; key = os.getenv("SHODAN_API_KEY")`
