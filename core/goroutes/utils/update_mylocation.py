from core.authentication.models import User
from asgiref.sync import sync_to_async

@sync_to_async
def update_mylocation(data):
    user_id = int(data["user_id"])
    user = User.objects.filter(id=user_id).first()

    if user:
        user.my_location = {
            "latitude": data["latitude"],
            "longitude": data["longitude"]
        }
        user.save()

        print("Localização salva:", data)
    else:
        print("Usuário não encontrado")
