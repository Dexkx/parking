from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated, AllowAny
from core.views.mixins import NestedRouterModelMixin, NewCreatedModelMixin
from clientes.permissions import JerarquiaPermission
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
            self.permission_classes = (IsAuthenticated, JerarquiaPermission)

        return super().get_permissions()

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user

        colab_fr = (
            user.franquicias
            .activos()
            .filter(
                franquicia= models.models.OuterRef('franquicia')
            )
        )

        colab_n = (
            user.negocios
            .activos()
            .filter(
                negocio= models.models.OuterRef('pk')
            )
        )

        return qs.filter(
            models.models.Q(models.models.Exists(colab_fr)) |
            models.models.Q(models.models.Exists(colab_n))
        )


class ColaboradoresNegocioViewSet(
    NestedRouterModelMixin, NewCreatedModelMixin, ModelViewSet
):
    """Colaboradores de un negocio. URL: /negocios/{nit}/colaboradores/"""

    queryset = models.ColaboradoresNegocio.objects.all()
    serializer_class = ColaboradoresNegocioSR
    permission_classes = (IsAuthenticated, JerarquiaPermission)
    lookup_field = "usuario"
    nested_instances = [
        {"lookup": "negocio", "field_name": "negocio", "model_class": models.Negocio}
    ]
