from mcp.server.fastmcp import FastMCP
from tools import get_latest_meeting_transcript as get_latest_meeting_transcript_impl

mcp = FastMCP("meet-mcp")


@mcp.tool()
def get_latest_meeting_transcript() -> dict:
    """Récupère le transcript de la dernière réunion.

    Mode démo uniquement (source="fixture") : lit un fichier transcript
    local (.txt ou .md) désigné par MEET_TRANSCRIPT_FIXTURE_PATH. Aucune
    donnée n'est présentée comme provenant d'un vrai service Meet/Visio.
    """
    return get_latest_meeting_transcript_impl()


if __name__ == "__main__":
    mcp.run()
