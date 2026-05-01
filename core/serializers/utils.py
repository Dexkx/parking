from .. import models
from rest_framework import serializers
from .mixins import StatusSRMixin

class TipoVehiculoSR(StatusSRMixin, serializers.ModelSerializer):
    """
    Serializer para el catálogo de tipos de vehículos.
    """

    class Meta:
        model = models.TipoVehiculo
        fields = ("id", "name")


class TipoIdentificacionSR(StatusSRMixin, serializers.ModelSerializer):
    """
    Serializer para el catálogo de tipos de identificación.
    """

    class Meta:
        model = models.TipoIdentificacion
        fields = ("descripcion", "value")


class TipoColaboradorSR(StatusSRMixin, serializers.ModelSerializer):
    """
    Serializer para el catálogo de tipos de colaborador.
    """

    class Meta:
        model = models.TipoColaborador
        fields = ("code", "descripcion")


class VehiculoUsuarioSR(StatusSRMixin, serializers.ModelSerializer):
    """
    Serializer para los vehículos registrados de un usuario.
    Se usa en la app para asociar placas a reservas.
    """

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["tipo_vehiculo"] = TipoVehiculoSR(instance.tipo_vehiculo).data
        return data

    class Meta:
        model = models.VehiculosUsuario
        fields = ("placa", "tipo_vehiculo")
