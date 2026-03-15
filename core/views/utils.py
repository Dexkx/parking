from .. import models
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from .. import serializers
from .mixins import NestedRouterModelMixin


class TipoVehiculoGetOnlyView(ListModelMixin, RetrieveModelMixin, GenericViewSet):
    queryset = models.TipoVehiculo.objects.all()
    serializer_class = serializers.TipoVehiculoSR


class TipoIdentificacionGetOnlyView(ListModelMixin, RetrieveModelMixin, GenericViewSet):
    queryset = models.TipoIdentificacion.objects.all()
    serializer_class = serializers.TipoIdentificacionSR


class TipoColaboradorGetOnlyView(ListModelMixin, RetrieveModelMixin, GenericViewSet):
    queryset = models.TipoColaborador.objects.all()
    serializer_class = serializers.TipoColaboradorSR


class PaisGetOnlyView(ListModelMixin, RetrieveModelMixin, GenericViewSet):
    queryset = models.Pais.objects.all()
    serializer_class = serializers.PaisSR


class DepartamentoGetOnlyView(ListModelMixin, RetrieveModelMixin, NestedRouterModelMixin, GenericViewSet):
    queryset = models.Departamento.objects.all()
    serializer_class = serializers.DepartamentoSR
    nested_instances = [
        {
            "lookup": "pais",
            "field_name": "pais",
            "model_class": models.Pais,
        },
    ]


class CidadGetOnlyView(ListModelMixin, RetrieveModelMixin, NestedRouterModelMixin, GenericViewSet):
    queryset = models.Ciudad.objects.all()
    serializer_class = serializers.CiudadSR
    nested_instances = [
        {
            "lookup": "departamento",
            "field_name": "departamento",
            "model_class": models.Departamento,
        },
        {
            "lookup": "pais",
            "field_name": "pais",
            "model_class": models.Pais,
        }
    ]
