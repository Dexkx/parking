from rest_framework import serializers
from .. import models
from core.models import Usuarios
from core.serializers import StatusSRMixin, TipoColaboradorSR, UsuarioSR, TipoVehiculoSR


class NegocioSR(StatusSRMixin, serializers.ModelSerializer):
    creado_por = serializers.PrimaryKeyRelatedField(
        queryset=Usuarios.objects.all(), write_only=True
    )
    nit = serializers.CharField(max_length=20)
    numero_verificacion = serializers.IntegerField()
    razon_social = serializers.CharField(max_length=225)
    puntuacion = serializers.FloatField(read_only=True)
    sedes_count = serializers.SerializerMethodField(read_only=True)

    def get_sedes_count(self, obj):
        return obj.sedes.activos().count()

    def to_representation(self, instance):
        data = super().to_representation(instance)
        # Incluir primera sede para el mapa (lat/lng)
        primera_sede = instance.sedes.activos().first()
        if primera_sede:
            data['lat'] = float(primera_sede.lat) if primera_sede.lat else None
            data['lng'] = float(primera_sede.lng) if primera_sede.lng else None
            data['direccion'] = primera_sede.direccion
            data['ciudad'] = CitySR(primera_sede.city).data
        return data

    class Meta:
        model = models.Negocio
        fields = (
            "nit", "numero_verificacion", "razon_social",
            "nombre", "creado_por", "puntuacion", "sedes_count",
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
        user = attrs.get('usuario')
        negocio = attrs.get('negocio')

        if negocio.is_owner(user):
            raise serializers.ValidationError("El dueño no puede agregarse como colaborador")

        return super().validate(attrs)

    class Meta:
        model = models.ColaboradoresNegocio
        fields = ('negocio', 'usuario', 'tipo_colaborador', 'status')


