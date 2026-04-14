from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated, AllowAny
from core.views.mixins import NestedRouterModelMixin, NewCreatedModelMixin
from clientes.permissions import IsNegocio
from .. import models
from ..serializers import NegocioSR, ColaboradoresNegocioSR, PuestoNegocioSR, TarifaNegocioSR


class NegocioViewSet(ModelViewSet):
    """
    CRUD de negocios (parqueaderos).
    - list/retrieve: público (mapa de la app)
    - create/update/delete: autenticado
    """
    queryset = models.Negocio.objects.all()
    serializer_class = NegocioSR

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            self.permission_classes = (AllowAny,)
        else:
            self.permission_classes = (IsAuthenticated,)
        return super().get_permissions()


class ColaboradoresNegocioViewSet(NestedRouterModelMixin, NewCreatedModelMixin, ModelViewSet):
    """
    Gestión de colaboradores de un negocio.
    URL: /negocios/{nit}/colaboradores/
    Solo el dueño/admin del negocio puede gestionar colaboradores.
    """
    queryset = models.ColaboradoresNegocio.objects.all()
    serializer_class = ColaboradoresNegocioSR
    permission_classes = (IsNegocio,)
    nested_instances = [
        {
            'lookup': 'negocio',
            'field_name': 'negocio_id',
            'model_class': models.Negocio,
        }
    ]


class PuestoNegocioViewSet(NestedRouterModelMixin, NewCreatedModelMixin, ModelViewSet):
    """
    Gestión de puestos de un negocio (piso + número + tipo vehículo).
    URL: /negocios/{nit}/puestos/
    Solo el dueño/admin del negocio puede parametrizar los puestos.
    """
    queryset = models.PuestoNegocio.objects.all()
    serializer_class = PuestoNegocioSR
    permission_classes = (IsNegocio,)
    nested_instances = [
        {
            'lookup': 'negocio',
            'field_name': 'negocio_id',
            'model_class': models.Negocio,
        }
    ]


class TarifasNegocioViewSet(NestedRouterModelMixin, NewCreatedModelMixin, ModelViewSet):
    """
    Gestión de tarifas de un negocio.
    URL: /negocios/{nit}/tarifas/
    Las tarifas pueden ser globales, por piso o por puesto específico.
    Solo el dueño/admin puede crear/modificar tarifas.
    """
    queryset = models.TarifasNegocio.objects.all()
    serializer_class = TarifaNegocioSR
    permission_classes = (IsNegocio,)
    nested_instances = [
        {
            'lookup': 'negocio',
            'field_name': 'negocio_id',
            'model_class': models.Negocio,
        }
    ]
