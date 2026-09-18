from mcp.server.fastmcp import FastMCP
from tools import organise_le_suivi as organise_le_suivi_impl

mcp = FastMCP("suivi-mcp")


@mcp.tool()
def organise_le_suivi(transcript: str) -> dict:
    """Organise le suivi d'une conversation Buzz collaborative : analyse le
    texte fourni avec le modèle local, crée un compte-rendu réel dans Docs
    (La Suite Numérique) et des lignes d'action réelles dans Grist.

    Utilise cet outil quand l'équipe demande à Mission Control d'"organiser
    le suivi" (ou une formulation équivalente).

    `transcript` DOIT être la conversation Buzz réelle et pertinente (les
    messages du canal/du fil actuel qui font l'objet du suivi) — ne jamais
    inventer, résumer au préalable, ou coder en dur un transcript de
    démonstration. Passe le texte des messages tel que reçu dans le contexte
    de cette conversation.

    Ne publie RIEN dans Buzz toi-même : cet outil ne fait qu'analyser et
    créer les artefacts réels (Docs + Grist). Une fois l'appel terminé, le
    champ `confirmation` du résultat est le texte à publier dans le canal
    Buzz courant, via le mécanisme de publication Buzz déjà existant
    (par exemple `buzz messages send`).

    Retourne un dict avec :
    - confirmation: texte prêt à publier dans Buzz
    - success: bool, False si Docs et/ou Grist a échoué
    - docs_document_id: id du document Docs créé, ou None si échec
    - grist_record_ids: liste des ids des lignes Grist créées
    - errors: dict optionnel {"docs": "...", "grist": "..."} en cas d'échec partiel
    """
    return organise_le_suivi_impl(transcript)


if __name__ == "__main__":
    mcp.run()
