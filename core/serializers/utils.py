from .. import models
from rest_framework import serializers


class TipoVehiculoSR(serializers.ModelSerializer):

    class Meta:
        model = models.TipoVehiculo
        fields = ("name", "llantas")


class TipoIdentificacionSR(serializers.ModelSerializer):

    class Meta:
        model = models.TipoIdentificacion
        fields = ("descripcion", "value")


class TipoColaboradorSR(serializers.ModelSerializer):

    class Meta:
        model = models.TipoColaborador
        fields = ("code", "descripcion")


class VehiculoUsuarioSR(serializers.ModelSerializer):
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
