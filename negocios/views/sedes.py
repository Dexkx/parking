from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework.permissions import AllowAny
from core.views.mixins import NestedRouterModelMixin, NewCreatedModelMixin
from clientes.permissions import JerarquiaPermission
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


class SedePublicViewSet(ReadOnlyModelViewSet):
    """
    Endpoint público para descubrimiento de sedes.
    URL: /sedes-publicas/
    Solo lectura, accesible por cualquiera, y filtra sedes sin tarifas.
    """

    queryset = models.Sede.objects.all()
    serializer_class = SedeSR
    permission_classes = [AllowAny]
    filterset_fields = {"negocio": ("exact",), "city": ("exact",)}

    def get_queryset(self):
        qs = super().get_queryset()

        puestos_compatibles = models.Puestos.objects.disponibles().filter(
            sede=models.models.OuterRef(models.models.OuterRef("pk")),
            tipo_vehiculo=models.models.OuterRef("tipo_vehiculo"),
            status__in=('Activo', 'Libre')
        )

        tarifas_con_puestos = models.Tarifas.objects.activos().filter(
            models.models.Q(sede=models.models.OuterRef("pk")) |
            models.models.Q(negocio=models.models.OuterRef("negocio"), sede__isnull=True),
            models.models.Exists(puestos_compatibles)
        )

        return (
            qs
            .activos()
            .filter(
                models.models.Exists(tarifas_con_puestos),
                negocio__status="Activo",
            )
            .distinct()
        )


class SedeViewSet(ModelViewSet):
    """
    Sedes de un negocio.
    URL: /sedes/

    Cada sede es una ubicación física del parqueadero.
    Un negocio puede tener N sedes distribuidas por la ciudad o el país.
    Solo el dueño/admin del negocio puede crear y gestionar sedes.
    """

    queryset = models.Sede.objects.all()
    permission_classes = (JerarquiaPermission,)
    serializer_class = SedeSR
    filterset_fields = {"negocio": ("exact",)}

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user

        colab_fr = (
            user.franquicias
            .activos()
            .filter(
                franquicia= models.models.OuterRef('negocio__franquicia')
            )
        )

        colab_n = (
            user.negocios
            .activos()
            .filter(
                negocio= models.models.OuterRef('negocio')
            )
        )

        colab_sd = (
            user.sedes
            .activos()
            .filter(
                sede= models.models.OuterRef('pk')
            )
        )

        return qs.filter(
            models.models.Q(models.models.Exists(colab_sd)) |
            models.models.Q(models.models.Exists(colab_n)) |
            models.models.Q(models.models.Exists(colab_fr))
        )

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
            self.permission_classes = (JerarquiaPermission,)
        return super().get_permissions()

    nested_instances = [
        {
            "lookup": "sede",
            "field_name": "sede",
            "model_class": models.Sede,
        }
    ]
