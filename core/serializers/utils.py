from .. import models
from ..models import Status
from rest_framework import serializers


class StatusSRMixin:
    status = serializers.PrimaryKeyRelatedField(
        queryset=Status.objects.all(), required=False
    )

    def get_field_names(self, declared_fields, info):
        fields = super().get_field_names(declared_fields, info)

        fields = list(fields)
        if "status" not in fields:
            fields.append("status")
        return fields


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


class PaisSR(serializers.ModelSerializer):

    class Meta:
        model = models.Pais
        fields = ("name",)


class DepartamentoSR(serializers.ModelSerializer):

    class Meta:
        model = models.Departamento
        fields = ("name",)


class CiudadSR(serializers.ModelSerializer):

    class Meta:
        model = models.Ciudad
        fields = ("name",)
