from urllib.parse import quote_plus

def gerar_link_maps(caminho):
    """
    Gera um link do Google Maps com a rota otimizada.

    Args:
        caminho: Lista de endereços no caminho, onde o primeiro é a origem e o último o destino.

    Returns:
        Link do Google Maps com a rota.
    """
    if not caminho or len(caminho) < 2:
        raise ValueError("Caminho insuficiente para gerar a rota.")

    def limpar_endereco(endereco: str) -> str:
        return endereco.replace('#', '').replace('&', '')

    origin = limpar_endereco(caminho[0])
    destination = limpar_endereco(caminho[-1])
    waypoints = [limpar_endereco(p) for p in caminho[1:-1]]

    base_url = "https://www.google.com/maps/dir/"

    params = {
        "api": "1",
        "origin": origin,
        "destination": destination,
        "travelmode": "driving"
    }

    if waypoints:
        params["waypoints"] = "|".join(waypoints)

    query = "&".join([f"{k}={quote_plus(str(v))}" for k, v in params.items()])
    return f"{base_url}?{query}"
