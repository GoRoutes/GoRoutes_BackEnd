from .save_coords_cache import salvar_coordenadas_no_cache
import googlemaps

def fazer_geocoding_api(self, endereco: str):
        """
        Faz geocoding via API Google como fallback
        """
        try:
            gmaps = googlemaps.Client(key=self.api_key)
            
            geocode_result = gmaps.geocode(endereco)
            
            if geocode_result:
                location = geocode_result[0]['geometry']['location']
                latitude = location['lat']
                longitude = location['lng']
                
                print(f"📍 API retornou coordenadas: {latitude}, {longitude}")
                
                salvar_coordenadas_no_cache(endereco, latitude, longitude)
                
                return (latitude, longitude)
            else:
                print(f"❌ API não encontrou endereço: {endereco}")
                return None
                
        except Exception as e:
            print(f"🚨 Erro na API Geocoding: {e}")
            return None