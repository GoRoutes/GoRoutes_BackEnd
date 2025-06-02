from core.authentication.models import Responsible

def get_responsible_data(self, obj):
        try:
            from core.authentication.serializers.infra import ResponsibleReadSerializer 
            responsible = obj.responsible
            data = ResponsibleReadSerializer(responsible).data
            data.pop('user', None)
            return data
        except Responsible.DoesNotExist:
            return None