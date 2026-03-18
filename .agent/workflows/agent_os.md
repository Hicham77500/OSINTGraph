---
description: Pipeline de spécification et d'implémentation selon le workflow Agent OS (Copilot/Antgravity)
---
# Workflow Agent OS pour Antgravity & GitHub Copilot

Ce workflow adapte la philosophie "Agent OS" pour votre environnement de travail avec **Antgravity** (idéal pour l'analyse globale de la base de code, l'extraction de patterns et la rédaction de spécifications (specs)) et **GitHub Copilot / VSCode** (idéal pour l'autocomplétion en temps réel et les requêtes ciblées dans le chat).

L'objectif est d'arrêter de répéter indéfiniment vos règles de code à l'IA, et de créer un "cerveau" local pour votre projet.

## 1. Initialisation de la documentation (Install)
Exécutez cette commande pour préparer la structure de vos standards dans votre projet.

// turbo
```powershell
New-Item -ItemType Directory -Force -Path ".agent\standards"
New-Item -ItemType Directory -Force -Path ".agent\specs"
New-Item -ItemType File -Force -Path ".agent\standards\README.md" -Value "# Standards du projet`n`nCe dossier contient les règles, patterns et conventions du projet. Incorporez ces fichiers dans vos prompts de contexte."
```

## 2. Découverte des Standards (Discover)
Pour que l'IA connaisse vos patterns architecturaux, utilisez l'existant. Demandez à Antgravity d'auditer votre code actuel pour formaliser les règles.

**Action Antgravity (copiez-collez ou ditez-moi ceci) :**
> "Analyse les fichiers principaux de ce projet. Identifie nos conventions de nommage, notre architecture globale, la manière dont nous gérons l'état (ou les erreurs) et nos patterns récurrents. Ensuite, documente le tout en créant des fichiers pertinents dans le dossier `.agent/standards/` (ex: `architecture.md`, `stack_technique.md`)."

**Action GitHub Copilot (dans VSCode) :**
Ouvrez un fichier qui représente parfaitement vos standards de qualité, ouvrez le Chat Copilot et demandez :
> *"Quels sont les patterns et règles de bon code utilisés dans ce fichier ? Génère un résumé au format markdown que je pourrai sauvegarder comme référence de qualité."*
Sauvegardez la réponse dans `.agent/standards/`.

## 3. Cadrage et Spécification (Shape)
Ne codez plus à l'aveugle. Avant d'implémenter une feature complexe, planifiez-la en forçant l'alignement sur vos standards.

**Action Antgravity :**
> "Je souhaite réaliser la fonctionnalité suivante : [VOTRE DESCRIPTION]. En te basant impérativement sur nos règles documentées dans `.agent/standards/`, rédige une spécification technique d'implémentation dans le fichier `.agent/specs/ma_feature.md`."

## 4. Implémentation avec le Contexte Injecté (Inject)
Maintenant que le plan et les règles sont écrits, passez à l'exécution.

**Dans GitHub Copilot Chat (VSCode) :**
Utilisez les variables de contexte (`#file` ou `@workspace`) pour injecter les standards.
> *"Code la fonctionnalité décrite dans `#file:ma_feature.md` en obéissant scrupuleusement aux règles d'architecture définies dans `#file:architecture.md`."*

**Avec Antgravity :**
> *"Lis la spécification `.agent/specs/ma_feature.md` et implémente la solution. Assure-toi de respecter nos standards documentés dans `.agent/standards/`."*

## 5. Alignement Continu de l'équipe
La documentation IA doit vivre avec votre code :
- Lorsqu'un nouveau développeur ou que vous-même ajustez la façon de faire, demandez à l'IA : *"Mets à jour le fichier de standards `xyz.md` avec cette nouvelle approche."*
- Gardez vos fichiers de standards concis (< 100 lignes) pour que le contexte IA soit optimisé en matière de tokens.
