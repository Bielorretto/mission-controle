# Mission Control

Projet de hackathon : donner à une IA les moyens d'agir comme un·e collègue omniscient·e
et omniprésent·e au sein d'une organisation, en la connectant directement aux outils de
travail — en particulier ceux de la **Suite Numérique** (DINUM) — via le protocole
**MCP** (Model Context Protocol), et en l'exposant dans **Buzz**, un outil de messagerie
d'équipe avec agents IA intégrés.

## Le problème

Quand plusieurs équipes ou ministères travaillent ensemble sur un projet commun, deux
frictions ralentissent tout le monde :

1. **L'information**
   - *Délai* : obtenir une information nécessite de la chercher soi-même (fouiller des
     documents, des archives) ou de la demander à quelqu'un — ce qui peut prendre
     quelques minutes comme plusieurs jours, selon la disponibilité de la personne, si
     l'archive existe encore, etc.
   - *Qualité* : l'information trouvée ou obtenue peut être périmée ou erronée (document
     obsolète, mauvais souvenir d'un collègue).
2. **L'automatisation** : une personne qui ne maîtrise pas un outil (Docs, Grist...) est
   bloquée ; une personne qui le maîtrise n'a pas forcément le temps ou l'envie de le
   faire elle-même.

## La réponse : un agent IA connecté en direct aux outils

Un agent IA qui peut lire et écrire directement dans les outils de travail élimine les
deux frictions à la fois :
- Il répond **instantanément**, avec la donnée **actuelle** (pas une copie périmée),
  puisqu'il va la chercher lui-même dans les vrais outils au moment de la question.
- Il **agit à la place de l'utilisateur** (créer un document, mettre à jour un tableau
  de suivi, partager un fichier) sur simple demande en langage naturel.

## Architecture

```
Buzz (messagerie + agents IA)
   │
   ├── Agent "Honey" (runtime Claude Code)
   │        │
   │        ├── MCP: docs-mcp  ──────────►  Docs (La Suite Numérique)
   │        │   (code maison, mcp-servers/docs-mcp/)
   │        │
   │        └── MCP: grist  ────────────►  Grist (self-hosté, édition complète)
   │            (serveur MCP officiel intégré à Grist, aucun code)
   │
   └── Authentification : Keycloak (realm `hackathon-dinum`)
        — identité partagée entre le login navigateur de Docs et les appels API du MCP
```

### Composants

| Dossier / outil | Rôle |
|---|---|
| `buzz/` | Buzz — messagerie d'équipe avec agents IA (clone de [block/buzz](https://github.com/block/buzz), vendored, dépôt séparé) |
| `docs/` | Docs — éditeur de documents collaboratif de la Suite Numérique ([suitenumerique/docs](https://github.com/suitenumerique/docs), vendored, dépôt séparé) |
| `mcp-servers/docs-mcp/` | Serveur MCP maison pour Docs : `create_document`, `list_documents`, `delete_document`, `write_document`, `read_document`, `share_document` |
| `mcp-servers/shared/` | Auth Keycloak partagée (`KeycloakAuth`), réutilisée par les futurs serveurs MCP |
| Grist | Base de données/tableur self-hosté (Docker), branché via **son propre serveur MCP officiel** (40+ outils : création de docs/tables, lecture/écriture de lignes, requêtes SQL/langage naturel, pages, widgets, pièces jointes...) |
| `transcription/` | Module d'ingestion de transcriptions de réunion (`.txt`/`.md`) — première étape du pipeline `Transcript → Analyse IA → Grist → Buzz` |

### Pourquoi deux approches différentes pour Docs et Grist ?

- **Docs** n'a pas de serveur MCP existant : `docs-mcp` a été écrit à la main, en
  s'authentifiant via Keycloak (OIDC resource server) contre l'API `external_api` de
  Docs.
- **Grist** (édition complète) expose **déjà** un serveur MCP officiel complet — pas de
  code à écrire, juste à l'activer (`GRIST_MCP_ENABLED=true`,
  `GRIST_FORCE_ENABLE_ENTERPRISE=true`) et à le brancher avec une clé API personnelle.

Cette différence est volontaire : avant d'écrire un serveur MCP pour un nouvel outil de
la Suite Numérique, toujours vérifier s'il n'en expose pas déjà un.

## Statut actuel

- ✅ Docs : création, lecture, modification, suppression et partage de documents,
  opérationnel de bout en bout depuis Buzz.
- ✅ Grist : serveur MCP officiel branché, disponible depuis Buzz.
- ✅ Agent Buzz "Honey" (runtime Claude Code) connecté aux deux.
- 🚧 Drive (stockage de fichiers) : en cours d'exploration sur une machine séparée
  (repo [suitenumerique/drive](https://github.com/suitenumerique/drive)).
- 🚧 Boucle complète transcription → résumé → suivi Grist : testée manuellement, pas
  encore automatisée en un seul outil.

## Démarrer en local

Chaque brique tourne indépendamment (voir le README de chaque dossier vendored pour le
détail) :

```bash
# Buzz (relay + app desktop)
cd buzz && source ./bin/activate-hermit && BUZZ_HEALTH_PORT=8085 just dev

# Docs
cd docs && docker compose up -d

# Grist
docker run -d --name grist -p 8484:8484 -v grist-data:/persist \
  -e GRIST_MCP_ENABLED=true -e GRIST_FORCE_ENABLE_ENTERPRISE=true \
  gristlabs/grist
```

Les serveurs MCP sont enregistrés au niveau utilisateur de Claude Code
(`claude mcp list` pour voir l'état actuel) — n'importe quel agent Buzz utilisant le
runtime **Claude Code** y a accès automatiquement.

⚠️ `mcp-servers/.env` et `mcp-servers/keycloak-backup/` contiennent des secrets locaux et
ne sont **pas** suivis par git — à reconfigurer sur chaque machine (voir
`mcp-servers/docs-mcp/tools.py` pour les variables attendues).
