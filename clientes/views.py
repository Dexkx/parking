from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from core.views.mixins import NestedRouterModelMixin, CompositeFKMixin, NewCreatedModelMixin
from .permissions import IsNegocio, JerarquiaPermission
from . import models
from negocios.models import Negocio, ColaboradoresNegocio, ColaboradresFranquicia
from .serializers import ClienteNegocioSR
from rest_condition import Or


class ClienteNegocioViewSet(NestedRouterModelMixin, CompositeFKMixin, NewCreatedModelMixin, ModelViewSet):
    """
    Gestión de clientes de un negocio.
    URL: /negocios/{nit}/clientes/

    Desde aquí el dueño del parqueadero puede:
    - Ver, registrar y dar de baja clientes
    - Los clientes con membresía mensual se gestionan desde aquí
    - Desde el frontend, el admin puede ver el historial de reservas y pagos por cliente
    """
    queryset = models.ClienteNegocio.objects.all()
    serializer_class = ClienteNegocioSR
    permission_classes = (Or(IsNegocio, JerarquiaPermission),)
    nested_instances = [
        {
            'lookup': 'negocio',
            'field_name': 'negocio',
            'model_class': Negocio,
        }
    ]

    url_params_required = [
        {
            'lookup': 'negocio',
            'field_name': 'negocio',
        },
        {
            'lookup': 'pk',
            'field_name': 'usuario',
        }
    ]

    def get_queryset(self):
        user = self.request.user
        qs = super().get_queryset()

        colab_fr = (
            ColaboradresFranquicia.objects.filter(
                usuario=user,
                franquicia=models.models.OuterRef("negocio__franquicia")
            )
        )

        colab_ng = (
            ColaboradoresNegocio.objects.filter(
                usuario=user,
                negocio=models.models.OuterRef("negocio")
            )
        )

        return (
            qs
            .filter(
                models.models.Q(models.models.Exists(colab_fr)) |
                models.models.Q(models.models.Exists(colab_ng))
            )
        )
