from mcp.server.fastmcp import FastMCP
from tools import get_records as get_records_impl
from tools import list_tables as list_tables_impl

mcp = FastMCP("grist-mcp")


@mcp.tool()
def list_tables() -> list:
    """Liste les tables du document Grist configuré, avec leurs colonnes.
    Utilise cet outil pour découvrir le schéma avant d'interroger des
    enregistrements (get_records)."""
    return list_tables_impl()


@mcp.tool()
def get_records(table_id: str = None) -> list:
    """Récupère tous les enregistrements réels d'une table Grist (la table de
    suivi des actions par défaut si table_id n'est pas précisé).

    Utilise cet outil quand on te demande d'analyser, de faire le bilan, des
    statistiques, ou l'état d'avancement du suivi opérationnel enregistré
    dans Grist (actions, responsables, échéances, statuts, dépendances).

    Ne calcule rien ici : cet outil retourne les données brutes telles
    qu'elles existent réellement dans Grist. C'est à toi de compter, filtrer
    et calculer les statistiques (total, terminées, en cours, bloquées, taux
    d'avancement, répartition par responsable, points de blocage...)
    uniquement à partir de ces données réelles — n'invente jamais un chiffre
    qui n'est pas dérivable des enregistrements retournés."""
    return get_records_impl(table_id)


if __name__ == "__main__":
    mcp.run()
