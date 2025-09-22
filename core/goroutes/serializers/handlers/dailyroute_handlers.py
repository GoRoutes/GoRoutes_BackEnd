from core.goroutes.serializers.infra import DailyRouteWriteSerializer, RouteRetrieveSerializer
from core.goroutes.models import Route

def get_data_of_route(route_id):
    """
    Prepares the route data for creating a DailyRoute.
    """
    route = Route.objects.get(id=route_id)
    serializer = RouteRetrieveSerializer(route)

    daily_route_data = {
        "name": serializer.data["name"],
        "date": serializer.data.get("date", "2024-02-02"),
        "route": route.id,
        "init_hour": serializer.data.get("init_hour"),
        "end_hour": serializer.data.get("end_hour"),
        "origin": serializer.data["origin"],
        "destination": serializer.data.get("destination"),
        "driver": serializer.data.get("driver", {}).get("id") if serializer.data.get("driver") else None,
        "vehicle": serializer.data.get("vehicle", {}).get("id") if serializer.data.get("vehicle") else None,
        "latitude_origin": serializer.data.get("latitude_origin"),
        "longitude_origin": serializer.data.get("longitude_origin"),
        "latitude_destination": serializer.data.get("latitude_destination"),
        "longitude_destination": serializer.data.get("longitude_destination"),
        "created_at": serializer.data.get("created_at"),
        "auto_recalculate": serializer.data.get("auto_recalculate"),
        "addresses": serializer.data.get("addresses", []),
        "optimized_route_url": serializer.data.get("optimized_route_url"),
        "overview_polyline": serializer.data.get("overview_polyline"),
        "markers": serializer.data.get("markers"),
        "coords_passageiros": serializer.data.get("coords_passageiros", []),
        "points": serializer.data.get("points", []),
        "is_active": serializer.data.get("is_active"),
        "original": serializer.data.get("original", True),
    }

    return daily_route_data
