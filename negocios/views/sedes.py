from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import AllowAny
from core.views.mixins import NestedRouterModelMixin, NewCreatedModelMixin
from clientes.permissions import IsNegocio, IsSede
from .. import models
from ..serializers import (
    NegocioSR,
    SedeSR,
    ColaboradoresNegocioSR,
    PuestoSR,
    TarifaSR,
    ColaboradoresSedeSR,
)
from rest_condition import Or


class SedeViewSet(ModelViewSet):
    """
    Sedes de un negocio.
    URL: /sedes/

    Cada sede es una ubicación física del parqueadero.
    Un negocio puede tener N sedes distribuidas por la ciudad o el país.
    Solo el dueño/admin del negocio puede crear y gestionar sedes.
    """

    queryset = models.Sede.objects.all()
    serializer_class = SedeSR

    def get_permissions(self):
        if self.action in ("list", "retrieve"):
            self.permission_classes = (AllowAny,)
        else:
            self.permission_classes = (IsSede,)
        return super().get_permissions()


class SedeNegocioNestedViewSet(
    NestedRouterModelMixin, NewCreatedModelMixin, ModelViewSet
):
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
        if self.action in ("list", "retrieve"):
            self.permission_classes = (AllowAny,)
        else:
            self.permission_classes = (Or(IsNegocio, IsSede),)
        return super().get_permissions()

    nested_instances = [
        {
            "lookup": "negocio",
            "field_name": "negocio",
            "model_class": models.Negocio,
        }
    ]


class ColaboradoresSedeViewSet(
    NestedRouterModelMixin, NewCreatedModelMixin, ModelViewSet
):
    """
    Colaboradores de una sede.
    URL: /sedes/{pk}/colaboradores/

    Cada colaborador es un usuario que trabaja en la sede.
    Solo el dueño/admin de la sede puede crear y gestionar colaboradores.
    """

    queryset = models.ColaboradoresSede.objects.all()
    serializer_class = ColaboradoresSedeSR
    lookup_field = "usuario"

    def get_permissions(self):
        if self.action in ("list", "retrieve"):
            self.permission_classes = (AllowAny,)
        else:
            self.permission_classes = (IsSede,)
        return super().get_permissions()

    nested_instances = [
        {
            "lookup": "sede",
            "field_name": "sede",
            "model_class": models.Sede,
        }
    ]
