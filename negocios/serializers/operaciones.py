from rest_framework import serializers
from .. import models
from core.serializers import StatusSRMixin, UsuarioSR, TipoVehiculoSR, EmptyStringAsNullMixin


class PuestoSR(StatusSRMixin, serializers.ModelSerializer):
    sede = serializers.PrimaryKeyRelatedField(
        queryset=models.Sede.objects.all(), write_only=True
    )

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["tipo_vehiculo"] = TipoVehiculoSR(instance.tipo_vehiculo).data
        return data

    class Meta:
        model = models.Puestos
        fields = ("sede", "piso", "numero", "tipo_vehiculo")


class TarifaSR(StatusSRMixin, EmptyStringAsNullMixin, serializers.ModelSerializer):
    negocio = serializers.PrimaryKeyRelatedField(
        queryset=models.Negocio.objects.all(), write_only=True
    )
    sede = serializers.PrimaryKeyRelatedField(
        queryset=models.Sede.objects.all(), write_only=True, allow_null=True
    )
    piso = serializers.CharField(max_length=20, required=False, allow_null=True)
    numero = serializers.IntegerField(required=False, allow_null=True)
    tipo_vehiculo = serializers.PrimaryKeyRelatedField(
        queryset=models.TipoVehiculo.objects.all()
    )

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["tipo_vehiculo"] = TipoVehiculoSR(instance.tipo_vehiculo).data
        return data

    class Meta:
        model = models.Tarifas
        fields = ("negocio", "sede", "piso", "numero", "tipo_vehiculo", "tiempo", "valor")


class ResenaSR(StatusSRMixin, serializers.ModelSerializer):
    negocio = serializers.PrimaryKeyRelatedField(
        queryset=models.Negocio.objects.all(), write_only=True
    )
    uuid = serializers.UUIDField(read_only=True)

    def to_representation(self, instance):
        data = super().to_representation(instance)

        data["usuario"] = UsuarioSR(instance.usuario).data

        return data

    class Meta:
        model = models.Resena
        fields = ("uuid", "negocio", "usuario", "texto", "puntuacion")


class ReservaSR(StatusSRMixin, serializers.ModelSerializer):
    uuid = serializers.UUIDField(read_only=True)
    negocio = serializers.PrimaryKeyRelatedField(
        queryset=models.Negocio.objects.all(), write_only=True
    )

    # Valor actualizado solo en negocios.signals.operaciones antes de guardar en la DB
    valor_pagado = serializers.DecimalField(
        max_digits=10, decimal_places=2, min_value=0.0, read_only=True
    )

    def to_representaion(self, instance):
        data = super().to_representation(instance)

        data["usuario"] = UsuarioSR(instance.usuario).data
        data["tipo_vehiculo"] = TipoVehiculoSR(instance.tipo_vehiculo).data

        return data

    class Meta:
        model = models.Reserva
        fields = (
            "uuid",
            "negocio",
            "piso",
            "numero",
            "tipo_vehiculo",
            "tiempo",
            "usuario",
            "placa",
            "hf_inicio",
            "hf_final",
            "valor_pagado",
            "valor_transferencia",
            "valor_tarjeta",
            "valor_efectivo",
        )
