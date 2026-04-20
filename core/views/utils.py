from .. import models
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from .. import serializers


class TipoVehiculoGetOnlyView(ListModelMixin, RetrieveModelMixin, GenericViewSet):
    queryset = models.TipoVehiculo.objects.all()
    serializer_class = serializers.TipoVehiculoSR

    filterset_fields = {
        'status': ('exact',)
    }


class TipoIdentificacionGetOnlyView(ListModelMixin, RetrieveModelMixin, GenericViewSet):
    queryset = models.TipoIdentificacion.objects.all()
    serializer_class = serializers.TipoIdentificacionSR

    filterset_fields = {
        'status': ('exact',)
    }


class TipoColaboradorGetOnlyView(ListModelMixin, RetrieveModelMixin, GenericViewSet):
    queryset = models.TipoColaborador.objects.all()
    serializer_class = serializers.TipoColaboradorSR

    filterset_fields = {
        'status': ('exact',)
    }

