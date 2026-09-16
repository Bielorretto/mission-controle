
from mcp.server.fastmcp import FastMCP
from tools import create_document as create_document_impl
from tools import delete_document as delete_document_impl
from tools import list_documents as list_documents_impl
from tools import write_document as write_document_impl
from tools import read_document as read_document_impl
from tools import share_document as share_document_impl

mcp = FastMCP("docs-mcp")


@mcp.tool()
def create_document(title: str, content: str = None) -> dict:
    """Crée un nouveau document dans Docs (La Suite Numérique), avec un contenu
    initial optionnel (texte/markdown)."""
    return create_document_impl(title, content)


@mcp.tool()
def list_documents(title: str = None) -> list:
    """Liste les documents dans Docs (La Suite Numérique), avec leur id et leur titre.
    Filtre par titre (recherche partielle) si fourni — utile pour retrouver l'id
    d'un document avant de le supprimer."""
    return list_documents_impl(title)


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