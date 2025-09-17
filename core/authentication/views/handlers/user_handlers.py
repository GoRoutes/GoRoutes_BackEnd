from rest_framework.response import Response
from rest_framework import status
from core.authentication.models import User
from django.db import transaction

@transaction.atomic
def destroy_user(request, user_id):
    try:
        user = User.objects.get(id=user_id)

        passenger = getattr(user, 'passenger', None)
        if passenger:
            addresses = list(passenger.address.all())
            passenger.delete()

            for addr in addresses:
                if not addr.passenger.exists() and not addr.drivers.exists():
                    addr.delete()

        driver = getattr(user, 'driver', None)
        if driver:
            addresses = list(driver.adresses.all())
            driver.delete()

            for addr in addresses:
                if not addr.passenger.exists() and not addr.drivers.exists():
                    addr.delete()

        responsible = getattr(user, 'responsible', None)
        if responsible:
            responsible.delete()

        user.delete()

        return Response(
            {"detail": "User, related records, and unused addresses deleted successfully"},
            status=status.HTTP_200_OK
        )

    except User.DoesNotExist:
        return Response({"detail": "User not found"}, status=status.HTTP_404_NOT_FOUND)
