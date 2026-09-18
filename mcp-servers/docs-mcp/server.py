
from mcp.server.fastmcp import FastMCP
from tools import create_document as create_document_impl
from tools import create_document_as_owner as create_document_as_owner_impl
from tools import delete_document as delete_document_impl
from tools import list_documents as list_documents_impl
from tools import write_document as write_document_impl
from tools import read_document as read_document_impl
from tools import share_document as share_document_impl
from tools import search_documents_as_owner as search_documents_as_owner_impl
from tools import get_document_content_as_owner as get_document_content_as_owner_impl

mcp = FastMCP("docs-mcp")


@mcp.tool()
def create_document(title: str, content: str = None) -> dict:
    """Crée un nouveau document dans Docs (La Suite Numérique), avec un contenu
    initial optionnel (texte/markdown)."""
    return create_document_impl(title, content)


@mcp.tool()
def create_document_as_owner(title: str, content: str) -> dict:
    """Crée un nouveau document dans Docs, visible immédiatement pour le compte
    de démo (impress). Utilise cet outil pour créer un rapport/bilan (par
    exemple à partir de données Grist) quand create_document échoue par
    manque d'authentification — c'est le chemin de création de document
    actuellement fonctionnel dans cet environnement."""
    return create_document_as_owner_impl(title, content)


@mcp.tool()
def list_documents(title: str = None) -> list:
    """Liste les documents dans Docs (La Suite Numérique), avec leur id et leur titre.
    Filtre par titre (recherche partielle) si fourni — utile pour retrouver l'id
    d'un document avant de le supprimer."""
    return list_documents_impl(title)


@mcp.tool()
def search_documents_as_owner(title: str = None) -> list:
    """Recherche/liste les documents Docs réels visibles par le compte de démo
    (impress), avec leur id et leur titre. Filtre par titre (recherche
    partielle) si fourni.

    Utilise cet outil (avec get_document_content_as_owner) quand on te demande
    de retrouver, consulter ou résumer une connaissance/un document existant
    dans Docs — c'est le chemin de recherche actuellement fonctionnel dans cet
    environnement (list_documents échoue par manque d'authentification).
    Ne réponds jamais en inventant un document ou son contenu : recherche-le
    réellement ici d'abord."""
    return search_documents_as_owner_impl(title)


@mcp.tool()
def get_document_content_as_owner(document_id: str) -> dict:
    """Lit le contenu réel d'un document Docs (en markdown), identifié par son
    id (obtenu via search_documents_as_owner). C'est le chemin de lecture
    actuellement fonctionnel dans cet environnement (read_document échoue par
    manque d'authentification)."""
    return get_document_content_as_owner_impl(document_id)


@mcp.tool()
def delete_document(document_id: str) -> dict:
    """Supprime un document dans Docs (La Suite Numérique) à partir de son id."""
    return delete_document_impl(document_id)


@mcp.tool()
def write_document(document_id: str, content: str) -> dict:
    """Remplace tout le contenu d'un document existant dans Docs (La Suite Numérique)
    par le texte/markdown fourni. Attention : ceci écrase le contenu existant,
    ce n'est pas un ajout."""
    return write_document_impl(document_id, content)


@mcp.tool()
def read_document(document_id: str) -> dict:
    """Lit le contenu d'un document dans Docs (La Suite Numérique) en markdown,
    pour le coller dans le chat ou le résumer."""
    return read_document_impl(document_id)


@mcp.tool()
def share_document(document_id: str, reach: str = "authenticated", role: str = "reader") -> dict:
    """Partage un document dans Docs (La Suite Numérique) via un lien.
    reach: 'restricted' (privé), 'authenticated' (tout utilisateur connecté),
    ou 'public'. role: 'reader', 'commenter', ou 'editor'."""
    return share_document_impl(document_id, reach, role)


if __name__ == "__main__":
    mcp.run()