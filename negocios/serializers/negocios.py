from rest_framework import serializers
from .. import models
from core.models import Usuarios
from core.serializers import StatusSRMixin, TipoColaboradorSR, UsuarioSR, TipoVehiculoSR, CitySR, EmptyStringAsNullMixin
from .franquicias import FranquiciasSR
from django.utils import timezone

class NegocioSR(EmptyStringAsNullMixin, StatusSRMixin, serializers.ModelSerializer):
    creado_por = serializers.PrimaryKeyRelatedField(
        queryset=Usuarios.objects.all(), write_only=True
    )
    nit = serializers.CharField(max_length=20)
    numero_verificacion = serializers.IntegerField()
    razon_social = serializers.CharField(max_length=225)
    puntuacion = serializers.FloatField(read_only=True)

    franquicia = serializers.PrimaryKeyRelatedField(
        queryset=models.Franquicias.objects.all(),
        required=False,
        allow_null=True,
    )

    reservas_hoy_count = serializers.SerializerMethodField(read_only=True)
    def get_reservas_hoy_count(self, obj):
        return obj.reservas.filter(hf_inicio__date=timezone.now().date()).count()

    sedes_count = serializers.SerializerMethodField(read_only=True)
    def get_sedes_count(self, obj):
        return obj.sedes.activos().count()

    minutos_gracia = serializers.IntegerField(required=False, allow_null=True)

    def to_representation(self, instance):
        data = super().to_representation(instance)

        if instance.franquicia is not None:
            data["franquicia"] = FranquiciasSR(instance.franquicia).data

        return data

    class Meta:
        model = models.Negocio
        fields = (
            "nit", "numero_verificacion", "razon_social",
            "nombre", "creado_por", "puntuacion", "sedes_count",
            "franquicia", "reservas_hoy_count", "minutos_gracia"
        )


class ColaboradoresNegocioSR(StatusSRMixin, serializers.ModelSerializer):
    negocio = serializers.PrimaryKeyRelatedField(
        queryset=models.Negocio.objects.all(), write_only=True
    )
    tipo_colaborador = serializers.PrimaryKeyRelatedField(
        queryset=models.TipoColaborador.objects.all()
    )

    status = serializers.BooleanField(required=False)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['usuario'] = UsuarioSR(instance.usuario).data
        data['tipo_colaborador'] = TipoColaboradorSR(instance.tipo_colaborador).data
        return data

    def validate(self, attrs):
        negocio = attrs.get('negocio')
        if (user := attrs.get('usuario')) and negocio.is_owner(user):
            raise serializers.ValidationError("El dueño no puede agregarse como colaborador")

        return super().validate(attrs)

    class Meta:
        model = models.ColaboradoresNegocio
        fields = ('negocio', 'usuario', 'tipo_colaborador', 'status')


