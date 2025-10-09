import requests
try:
    from django.conf import settings
except ImportError:
    settings = None

def get_latitude_longitude(address):
    """
    Get latitude and longitude from address using Google Maps API
    """
    api_key = settings.GOOGLE_MAPS_API_KEY
    url = f"https://maps.googleapis.com/maps/api/geocode/json?address={address}&key={api_key}"
    
    try:
        response = requests.get(url)
        data = response.json()
        
        if data["status"] == "OK":
            location = data["results"][0]["geometry"]["location"]
            return location["lat"], location["lng"]
        return None, None
    except Exception as e:
        print(f"Error getting latitude and longitude: {e}")
        return None, None