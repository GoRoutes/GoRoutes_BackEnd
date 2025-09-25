import requests
from typing import List, Dict, Any

from .get_links_maps import gerar_link_maps


def fetch_directions(origin: str, destination: str, waypoints: List[str], api_key: str) -> Dict[str, Any]:

    if not origin or not destination:
        raise ValueError("Origin e destination são obrigatórios")

    if not isinstance(waypoints, list):
        raise ValueError("Waypoints deve ser uma lista de endereços")

    url = "https://maps.googleapis.com/maps/api/directions/json"
    params = {
        "origin": origin,
        "destination": destination,
        "waypoints": ("optimize:true|" + "|".join(waypoints)) if waypoints else None,
        "region": "br",
        "language": "pt-BR",
        "key": api_key,
    }

    params = {k: v for k, v in params.items() if v is not None}

    response = requests.get(url, params=params)
    data = response.json()

    if data.get("status") != "OK":
        raise ValueError(f"Directions API retornou status '{data.get('status')}'")

    route = data["routes"][0]

    waypoint_order = route.get("waypoint_order", [])
    ordered_addresses = waypoints
    if waypoints and waypoint_order:
        ordered_addresses = [waypoints[i] for i in waypoint_order]

    points: List[str] = []
    for leg in route.get("legs", []):
        for step in leg.get("steps", []):
            poly = step.get("polyline", {})
            p = poly.get("points")
            if p:
                points.append(p)

    overview_polyline = route.get("overview_polyline", {})

    caminho = [origin] + (ordered_addresses or []) + [destination]
    link_maps = gerar_link_maps(caminho)

    return {
        "ordered_addresses": ordered_addresses,
        "overview_polyline": overview_polyline,
        "points": points,
        "link_maps": link_maps,
    }


