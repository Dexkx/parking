from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated, AllowAny
from core.views.mixins import (
    NestedRouterModelMixin,
    NewCreatedModelMixin,
    CompositeFKMixin,
)
from clientes.permissions import IsCliente, IsNegocio, IsSede
from .. import models
from ..serializers import ResenaSR, ReservaSR, PuestoSR, TarifaSR


class PuestoSedeViewSet(
    NestedRouterModelMixin, CompositeFKMixin, NewCreatedModelMixin, ModelViewSet
):
    """
    Puestos de una sede específica.
    URL: /sedes/{uuid}/puestos/
    """

    queryset = models.Puestos.objects.all()
    serializer_class = PuestoSR
    permission_classes = (IsSede,)
    nested_instances = [
        {"lookup": "sede", "field_name": "sede", "model_class": models.Sede}
    ]

    url_params_required = (
        {
            "lookup": "piso",
            "field_name": "piso",
        },
        {
            "lookup": "numero",
            "field_name": "numero",
        },
        {
            "lookup": "tipo_vehiculo",
            "field_name": "tipo_vehiculo",
        },
    )


class TarifasSedeViewSet(NestedRouterModelMixin, NewCreatedModelMixin, ModelViewSet):
    """
    Tarifas de una sede.
    URL: /sedes/{uuid}/tarifas/
    """

    queryset = models.Tarifas.objects.all()
    serializer_class = TarifaSR
    permission_classes = (IsSede,)
    nested_instances = [
        {"lookup": "sede", "field_name": "sede", "model_class": models.Sede}
    ]


class ResenaViewSet(NestedRouterModelMixin, NewCreatedModelMixin, ModelViewSet):
    """
    Reseñas de un parqueadero.
    URL: /negocios/{nit}/resenas/
    - list/retrieve: público
    - create: solo clientes registrados del negocio
    - update/delete: autenticado (dueño de la reseña o admin)
    """

    queryset = models.Resena.objects.all()
    serializer_class = ResenaSR
    nested_instances = [
        {
            "lookup": "negocio",
            "field_name": "negocio_id",
            "model_class": models.Negocio,
        }
    ]

    def get_permissions(self):
        if self.action in ("list", "retrieve"):
            self.permission_classes = (AllowAny,)
        elif self.action == "create":
            self.permission_classes = (IsCliente,)
        else:
            self.permission_classes = (IsAuthenticated,)
        return super().get_permissions()


class ReservaViewSet(NestedRouterModelMixin, NewCreatedModelMixin, ModelViewSet):
    """
    Reservas de un parqueadero.
    URL: /negocios/{nit}/reservas/
    - Clientes: solo ven sus propias reservas
    - Negocio (dueño/admin): ven todas las reservas de su negocio
    Autenticación requerida para todas las operaciones.
    """

    queryset = models.Reserva.objects.all()
    serializer_class = ReservaSR
    permission_classes = (IsAuthenticated,)
    nested_instances = [
        {
            "lookup": "negocio",
            "field_name": "negocio_id",
            "model_class": models.Negocio,
        }
    ]

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user

        if user.is_negocio:
            return qs

        return qs.filter(usuario=user)
