from rest_framework import serializers
from .. import models
from core.serializers import StatusSRMixin, UsuarioSR, TipoVehiculoSR, EmptyStringAsNullMixin, Status
from core.models import Status
from .negocios import NegocioSR
from .sedes import SedeSR

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
    uuid = serializers.UUIDField(read_only=True)

    negocio = serializers.PrimaryKeyRelatedField(
        queryset=models.Negocio.objects.all(), write_only=True
    )
    sede = serializers.PrimaryKeyRelatedField(
        queryset=models.Sede.objects.all(), write_only=True, allow_null=True, required=False,
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
        fields = ("uuid", "negocio", "sede", "piso", "numero", "tipo_vehiculo", "tiempo", "valor")


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
        queryset=models.Negocio.objects.all()
    )
    sede = serializers.PrimaryKeyRelatedField(
        queryset=models.Sede.objects.all()
    )
    piso = serializers.CharField(max_length=20, required=False, allow_null=True) # Si es null se escoje el primer registro encontrado en validate()
    numero = serializers.IntegerField(required=False, allow_null=True) # Si es null se escoje el primer registro encontrado en validate()

    tarifa = serializers.PrimaryKeyRelatedField(
        queryset=models.Tarifas.objects.all(), write_only=True
    )

    # Valor actualizado solo en negocios.signals.operaciones antes de guardar en la DB
    valor_pagado = serializers.DecimalField(
        max_digits=10, decimal_places=2, min_value=0.0, read_only=True
    )

    def to_representation(self, instance):
        data = super().to_representation(instance)

        data["negocio"] = NegocioSR(instance.negocio).data
        data["sede"] = SedeSR(instance.sede).data

        data["usuario"] = UsuarioSR(instance.usuario).data
        data["tipo_vehiculo"] = TipoVehiculoSR(instance.tipo_vehiculo).data
        data["tarifa"] = TarifaSR(instance.tarifa).data

        return data

    def validate(self, attrs):
        #  Si ya existe la instancia (es un update), no buscamos puesto ni cambiamos el estado
        if self.instance:
            return super().validate(attrs)

        puestos_disponibles = (
            models.Puestos.objects.disponibles()
            .filter(
                sede=attrs.get("sede"),
                tipo_vehiculo=attrs.get("tipo_vehiculo"),
            )
        )
        if not puestos_disponibles.exists():
            raise serializers.ValidationError("No hay puestos disponibles para este tipo de vehículo")

        puesto = puestos_disponibles.first()
        if puesto:
            attrs["piso"] = puesto.piso


        numero = attrs.get("numero")
        if numero is None:
            attrs["numero"] = puesto.numero

        attrs["status"] = Status.RESERVADO
        return super().validate(attrs)

    class Meta:
        model = models.Reserva
        fields = (
            "uuid",
            "negocio",
            "sede",
            "piso",
            "numero",
            "tipo_vehiculo",
            "tarifa",
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
