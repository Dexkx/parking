from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated, AllowAny
from core.views.mixins import NestedRouterModelMixin, NewCreatedModelMixin
from clientes.permissions import IsNegocio
from .. import models
from ..serializers import (
    NegocioSR,
    ColaboradoresNegocioSR,
)


class NegocioViewSet(ModelViewSet):
    """CRUD de negocios. List/retrieve público (para el mapa), resto autenticado."""

    queryset = models.Negocio.objects.all()
    serializer_class = NegocioSR
    filterset_fields = {
        "franquicia": ("exact",)
    }

    def get_permissions(self):
        if self.action in ("list", "retrieve"):
            self.permission_classes = (AllowAny,)
        else:
            self.permission_classes = (IsAuthenticated,)
        return super().get_permissions()


class ColaboradoresNegocioViewSet(
    NestedRouterModelMixin, NewCreatedModelMixin, ModelViewSet
):
    """Colaboradores de un negocio. URL: /negocios/{nit}/colaboradores/"""

    queryset = models.ColaboradoresNegocio.objects.all()
    serializer_class = ColaboradoresNegocioSR
    permission_classes = (IsNegocio,)
    lookup_field = "usuario"
    nested_instances = [
        {"lookup": "negocio", "field_name": "negocio", "model_class": models.Negocio}
    ]
