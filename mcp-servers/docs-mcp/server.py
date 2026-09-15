
from mcp.server.fastmcp import FastMCP
from tools import create_document as create_document_impl

mcp = FastMCP("docs-mcp")


@mcp.tool()
def create_document(title: str) -> dict:
    """Crée un nouveau document dans Docs (La Suite Numérique)."""
    return create_document_impl(title)


if __name__ == "__main__":
    mcp.run()