# Mission Control

Projet de hackathon : construire, dans **Tchap** (la messagerie sécurisée de l'État),
un écosystème où **agents IA et humains cohabitent et travaillent ensemble** sur des
projets concrets — pas une IA à qui l'on pose des questions dans son coin, mais une
collègue à part entière, avec accès au contexte global de l'équipe, connectée en
direct aux outils de travail (en particulier ceux de la **Suite Numérique**, DINUM) via
le protocole **MCP** (Model Context Protocol). **Buzz**, une messagerie d'équipe avec
agents IA intégrés, sert de prototype de travail pour ce hackathon.

## Le problème

Aujourd'hui, tout le monde utilise déjà massivement l'IA au travail — mais chacun dans
son coin, avec son propre modèle, qui n'a accès qu'à **son** contexte personnel, jamais
à celui du groupe. Chaque personne a sa propre conversation isolée avec sa propre IA ;
la connaissance et les décisions qui en sortent restent enfermées dans ces échanges
individuels, invisibles pour le reste de l'équipe. Un projet commun avance donc avec
autant de versions fragmentées de la réalité qu'il y a de personnes qui utilisent
chacune leur IA séparément.

Cette fragmentation se traduit concrètement par deux frictions, en particulier quand
plusieurs équipes ou ministères travaillent ensemble :

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

## La réponse : un écosystème partagé, pas un chatbot

Mission Control n'est pas une interaction bilatérale (je demande une info à un bot, je
la récupère). L'objectif est que l'agent IA vive **dans l'espace de travail commun**, au
même endroit que les humains, avec accès au **contexte global du projet** — pas
seulement à ce qu'une seule personne lui a raconté dans son coin. Concrètement, ça lui
permet de :

- suivre et interagir naturellement dans les discussions de groupe, pas seulement
  répondre à qui l'interpelle directement,
- proposer des choses de sa propre initiative (pas uniquement réagir à une question),
- aider à obtenir ou vérifier une information pour **toute l'équipe** en même temps,
  avec une donnée toujours à jour puisqu'il va la chercher lui-même dans les vrais
  outils au moment voulu,
- agir directement sur les outils partagés (créer un document, mettre à jour un
  tableau de suivi, partager un fichier) au nom du groupe, sur simple demande en
  langage naturel.

L'IA cesse d'être un outil personnel isolé pour devenir un membre à part entière de
l'équipe, avec la même vue d'ensemble que tout le monde.

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
