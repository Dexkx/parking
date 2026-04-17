from rest_framework import serializers
from .. import models
from core.models import Usuarios
from core.serializers import PaisSR, CiudadSR, DepartamentoSR, StatusSRMixin, TipoColaboradorSR, UsuarioSR, TipoVehiculoSR


class NegocioSR(StatusSRMixin, serializers.ModelSerializer):
    creado_por = serializers.PrimaryKeyRelatedField(
        queryset=Usuarios.objects.all(), write_only=True
    )
    nit = serializers.CharField(max_length=20, write_only=True)
    numero_verificacion = serializers.IntegerField(write_only=True)
    razon_social = serializers.CharField(max_length=225, write_only=True)
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
            data['ciudad'] = CiudadSR(primera_sede.ciudad).data
        return data

    class Meta:
        model = models.Negocio
        fields = (
            "nit", "numero_verificacion", "razon_social",
            "nombre", "creado_por", "puntuacion", "sedes_count",
        )


class SedeSR(StatusSRMixin, serializers.ModelSerializer):
    """Serializer para sedes de un negocio."""
    uuid = serializers.UUIDField(read_only=True)
    negocio = serializers.PrimaryKeyRelatedField(
        queryset=models.Negocio.objects.all(), write_only=True
    )
    puntuacion = serializers.FloatField(read_only=True)
    puestos_count = serializers.SerializerMethodField(read_only=True)

    def get_puestos_count(self, obj):
        return obj.puestos.activos().count()

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['ciudad'] = CiudadSR(instance.ciudad).data
        data['departamento'] = DepartamentoSR(instance.departamento).data
        data['pais'] = PaisSR(instance.pais).data
        if instance.lat:
            data['lat'] = float(instance.lat)
        if instance.lng:
            data['lng'] = float(instance.lng)
        return data

    class Meta:
        model = models.Sede
        fields = (
            "uuid", "negocio", "nombre", "direccion",
            "pais", "departamento", "ciudad",
            "lat", "lng", "puntuacion", "puestos_count",
        )


class ColaboradoresNegocioSR(StatusSRMixin, serializers.ModelSerializer):
    negocio = serializers.PrimaryKeyRelatedField(
        queryset=models.Negocio.objects.all(), write_only=True
    )

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['usuario'] = UsuarioSR(instance.usuario).data
        data['tipo_colaborador'] = TipoColaboradorSR(instance.tipo_colaborador).data
        return data

    class Meta:
        model = models.ColaboradoresNegocio
        fields = ('negocio', 'usuario', 'tipo_colaborador')


class PuestoNegocioSR(StatusSRMixin, serializers.ModelSerializer):
    sede = serializers.PrimaryKeyRelatedField(
        queryset=models.Sede.objects.all(), write_only=True
    )

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['tipo_vehiculo'] = TipoVehiculoSR(instance.tipo_vehiculo).data
        return data

    class Meta:
        model = models.PuestoNegocio
        fields = ('sede', 'piso', 'numero', 'tipo_vehiculo')


class TarifaNegocioSR(StatusSRMixin, serializers.ModelSerializer):
    sede = serializers.PrimaryKeyRelatedField(
        queryset=models.Sede.objects.all(), write_only=True
    )
    piso = serializers.CharField(max_length=20, required=False, allow_null=True)
    numero = serializers.IntegerField(required=False, allow_null=True)
    tipo_vehiculo = serializers.PrimaryKeyRelatedField(
        queryset=models.TipoVehiculo.objects.all()
    )

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['tipo_vehiculo'] = TipoVehiculoSR(instance.tipo_vehiculo).data
        return data

    class Meta:
        model = models.TarifasNegocio
        fields = ('sede', 'piso', 'numero', 'tipo_vehiculo', 'tiempo', 'valor')
