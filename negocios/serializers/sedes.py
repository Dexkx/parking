from rest_framework import serializers
from .. import models
from core.models import Usuarios, Cities
from core.serializers import (
    CountrySR,
    CitySR,
    StateSR,
    StatusSRMixin,
    TipoColaboradorSR,
    UsuarioSR,
    TipoVehiculoSR,
    EmptyStringAsNullMixin,
)
from .negocios import NegocioSR


class SedeSR(EmptyStringAsNullMixin, StatusSRMixin, serializers.ModelSerializer):
    """Serializer para sedes de un negocio."""

    uuid = serializers.UUIDField(read_only=True)
    negocio = serializers.PrimaryKeyRelatedField(
        queryset=models.Negocio.objects.all()
    )
    puntuacion = serializers.FloatField(read_only=True)

    puestos_count = serializers.SerializerMethodField(read_only=True)
    def get_puestos_count(self, obj):
        return obj.puestos.activos().count()

    city = serializers.PrimaryKeyRelatedField(
        queryset=Cities.objects.all(), required=False, allow_null=True
    )

    lat = serializers.DecimalField(
        max_digits=10, decimal_places=7, required=False, allow_null=True
    )
    lng = serializers.DecimalField(
        max_digits=10, decimal_places=7, required=False, allow_null=True
    )

    creado_por = serializers.PrimaryKeyRelatedField(
        queryset=Usuarios.objects.all(), write_only=True
    )

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["negocio"] = NegocioSR(instance.negocio).data
        data["city"] = CitySR(instance.city).data
        data["state"] = StateSR(instance.state).data
        data["country"] = CountrySR(instance.country).data
        if instance.lat:
            data["lat"] = float(instance.lat)
        if instance.lng:
            data["lng"] = float(instance.lng)
        return data

    class Meta:
        model = models.Sede
        fields = (
            "uuid",
            "negocio",
            "nombre",
            "direccion",
            "country",
            "state",
            "city",
            "lat",
            "lng",
            "puntuacion",
            "puestos_count",
            "creado_por",
        )


class ColaboradoresSedeSR(StatusSRMixin, serializers.ModelSerializer):
    sede = serializers.PrimaryKeyRelatedField(
        queryset=models.Sede.objects.all(), write_only=True
    )
    usuario = serializers.PrimaryKeyRelatedField(queryset=Usuarios.objects.all())
    tipo_colaborador = serializers.PrimaryKeyRelatedField(
        queryset=models.TipoColaborador.objects.all()
    )
    status = serializers.BooleanField(required=False)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["usuario"] = UsuarioSR(instance.usuario).data
        data["tipo_colaborador"] = TipoColaboradorSR(instance.tipo_colaborador).data
        return data

    def validate(self, attrs):
        sede = attrs.get("sede")
        if (user := attrs.get('usuario')) and sede.is_owner(user):
            raise serializers.ValidationError(
                "El dueño no puede agregarse como colaborador"
            )

        return super().validate(attrs)

    class Meta:
        model = models.ColaboradoresSede
        fields = ("sede", "usuario", "tipo_colaborador", "status")
