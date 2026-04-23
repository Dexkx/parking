from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework.permissions import IsAuthenticated, AllowAny
from core.views.mixins import (
    NestedRouterModelMixin,
    NewCreatedModelMixin,
    CompositeFKMixin,
)
from clientes.permissions import IsCliente, IsNegocio, IsSede
from .. import models
from ..serializers import ResenaSR, ReservaSR, PuestoSR, TarifaSR
from rest_condition import Or

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
    permission_classes = (IsSede,)
    serializer_class = TarifaSR
    nested_instances = [
        {"lookup": "sede", "field_name": "sede", "model_class": models.Sede}
    ]

class TarifasPublicasList(NestedRouterModelMixin, ReadOnlyModelViewSet):
    """
    Tarifas públicas de todas las sedes.
    URL: /sedes-publicas/{uuid}/tarifas/
    """
    permission_classes = (AllowAny,)
    serializer_class = TarifaSR

    nested_instances = [
        {"lookup": "sede_publica", "field_name": "sede", "model_class": models.Sede}
    ]

    def get_queryset(self):
        sede_instance = self.get_param_query(instance_model=True).get('sede')
        if not sede_instance:
            return models.Tarifas.objects.none()

        tipo_vehiculos_puestos = (
            sede_instance.puestos
            .disponibles()
            .filter(
                tipo_vehiculo=models.models.OuterRef("tipo_vehiculo")
            )
        )

        qs = models.Tarifas.objects.activos().filter(
            models.models.Q(sede=sede_instance) |
            models.models.Q(negocio=sede_instance.negocio, sede__isnull=True),
            models.models.Exists(tipo_vehiculos_puestos),
        )

        # Definir la jerarquía de prioridad: Numero (4) > Piso (3) > Sede (2) > Negocio (1)
        priority_case = models.models.Case(
            models.models.When(numero__isnull=False, then=models.models.Value(4)),
            models.models.When(piso__isnull=False, then=models.models.Value(3)),
            models.models.When(sede__isnull=False, then=models.models.Value(2)),
            default=models.models.Value(1),
            output_field=models.models.IntegerField(),
        )

        # Ordenar y aplicar distinct para quedarse con la más específica por (vehículo, tiempo)
        return (
            qs.annotate(priority=priority_case)
            .order_by('tipo_vehiculo', 'tiempo', '-priority')
            .distinct('tipo_vehiculo', 'tiempo')
        )

class TarifasNegocioViewSet(NestedRouterModelMixin, NewCreatedModelMixin, ModelViewSet):
    """
    Tarifas de un negocio.
    URL: /negocios/{nit}/tarifas/
    """

    queryset = models.Tarifas.objects.all()
    serializer_class = TarifaSR
    permission_classes = (IsNegocio,)
    nested_instances = [
        {"lookup": "negocio", "field_name": "negocio", "model_class": models.Negocio}
    ]

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(
            sede__isnull=True,
            piso__isnull=True,
            numero__isnull=True,
        )


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
    URL: /sedes/{uuid}/reservas/
    - Clientes: solo ven sus propias reservas
    - Negocio (dueño/admin): ven todas las reservas de su negocio
    Autenticación requerida para todas las operaciones.
    """

    queryset = models.Reserva.objects.all()
    serializer_class = ReservaSR
    permission_classes = (IsAuthenticated,)
    nested_instances = [
        {
            "lookup": "sede",
            "field_name": "sede",
            "model_class": models.Sede,
        }
    ]

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user

        # if user.is_negocio:
        #     return qs

        return qs.filter(usuario=user)


    def create(self, request, *args, **kwargs):
        request.data["usuario"] = request.user.pk
        return super().create(request, *args, **kwargs)
