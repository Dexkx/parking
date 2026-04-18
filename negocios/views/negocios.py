from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated, AllowAny
from core.views.mixins import NestedRouterModelMixin, NewCreatedModelMixin
from clientes.permissions import IsNegocio
from .. import models
from ..serializers import NegocioSR, SedeSR, ColaboradoresNegocioSR, PuestoNegocioSR, TarifaNegocioSR


class NegocioViewSet(ModelViewSet):
    """CRUD de negocios. List/retrieve público (para el mapa), resto autenticado."""
    queryset = models.Negocio.objects.all()
    serializer_class = NegocioSR

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            self.permission_classes = (AllowAny,)
        else:
            self.permission_classes = (IsAuthenticated,)
        return super().get_permissions()


class SedeViewSet(NestedRouterModelMixin, NewCreatedModelMixin, ModelViewSet):
    """
    Sedes de un negocio.
    URL: /negocios/{nit}/sedes/

    Cada sede es una ubicación física del parqueadero.
    Un negocio puede tener N sedes distribuidas por la ciudad o el país.
    Solo el dueño/admin del negocio puede crear y gestionar sedes.
    """
    queryset = models.Sede.objects.all()
    serializer_class = SedeSR

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            self.permission_classes = (AllowAny,)
        else:
            self.permission_classes = (IsNegocio,)
        return super().get_permissions()

    nested_instances = [
        {
            'lookup': 'negocio',
            'field_name': 'negocio',
            'model_class': models.Negocio,
        }
    ]


class ColaboradoresNegocioViewSet(NestedRouterModelMixin, NewCreatedModelMixin, ModelViewSet):
    """Colaboradores de un negocio. URL: /negocios/{nit}/colaboradores/"""
    queryset = models.ColaboradoresNegocio.objects.all()
    serializer_class = ColaboradoresNegocioSR
    permission_classes = (IsNegocio,)
    nested_instances = [
        {'lookup': 'negocio', 'field_name': 'negocio_id', 'model_class': models.Negocio}
    ]


class PuestoNegocioViewSet(NestedRouterModelMixin, NewCreatedModelMixin, ModelViewSet):
    """
    Puestos de una sede específica.
    URL: /negocios/{nit}/sedes/{uuid}/puestos/
    """
    queryset = models.PuestoNegocio.objects.all()
    serializer_class = PuestoNegocioSR
    permission_classes = (IsNegocio,)
    nested_instances = [
        {'lookup': 'sede', 'field_name': 'sede_id', 'model_class': models.Sede}
    ]


class TarifasNegocioViewSet(NestedRouterModelMixin, NewCreatedModelMixin, ModelViewSet):
    """
    Tarifas de una sede.
    URL: /negocios/{nit}/sedes/{uuid}/tarifas/
    """
    queryset = models.TarifasNegocio.objects.all()
    serializer_class = TarifaNegocioSR
    permission_classes = (IsNegocio,)
    nested_instances = [
        {'lookup': 'sede', 'field_name': 'sede_id', 'model_class': models.Sede}
    ]
