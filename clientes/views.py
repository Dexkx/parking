from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from core.views.mixins import NestedRouterModelMixin, NewCreatedModelMixin
from .permissions import IsNegocio
from .models import ClienteNegocio
from .serializers import ClienteNegocioSR


class ClienteNegocioViewSet(NestedRouterModelMixin, NewCreatedModelMixin, ModelViewSet):
    """
    Gestión de clientes de un negocio.
    URL: /negocios/{nit}/clientes/

    Desde aquí el dueño del parqueadero puede:
    - Ver, registrar y dar de baja clientes
    - Los clientes con membresía mensual se gestionan desde aquí
    - Desde el frontend, el admin puede ver el historial de reservas y pagos por cliente
    """
    queryset = ClienteNegocio.objects.all()
    serializer_class = ClienteNegocioSR
    permission_classes = (IsNegocio,)
    nested_instances = [
        {
            'lookup': 'negocio',
            'field_name': 'negocio_id',
            'model_class': __import__('negocios.models', fromlist=['Negocio']).Negocio,
        }
    ]
