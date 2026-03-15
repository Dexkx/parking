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

    def to_representation(self, instance):
        data = super().to_representation(instance)

        data["pais"] = PaisSR(instance.pais).data
        data["departamento"] = DepartamentoSR(instance.departamento).data
        data["ciudad"] = CiudadSR(instance.ciudad).data

        return data

    class Meta:
        model = models.Negocio
        fields = (
            "nit",
            "numero_verificacion",
            "razon_social",
            "nombre",
            "direccion",
            "pais",
            "departamento",
            "ciudad",
            "creado_por",
        )


class ColaboradoresNegocioSR(StatusSRMixin, serializers.ModelSerializer):
    negocio = serializers.PrimaryKeyRelatedField(queryset=models.Negocio.objects.all(), write_only=True)
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        
        data['usuario'] = UsuarioSR(instance.usuario).data
        data['tipo_colaborador'] = TipoColaboradorSR(instance.tipo_colaborador).data
        
        return data

    class Meta:
        model = models.ColaboradoresNegocio
        fields = ('negocio', 'usuario', 'tipo_colaborador')


class PuestoNegocioSR(StatusSRMixin, serializers.ModelSerializer):
    negocio = serializers.PrimaryKeyRelatedField(queryset=models.Negocio.objects.all(), write_only=True)
    
    def to_representantion(self, instance):
        data = super().to_representation(instance)
        
        data['tipo_vehiculo'] = TipoVehiculoSR(instance.tipo_vehiculo).data
        
        return data
    
    class Meta:
        model = models.PuestoNegocio
        fields = ('negocio', 'piso', 'numero', 'tipo_vehiculo')

    
class TarifaNegocioSR(StatusSRMixin, serializers.ModelSerializer):
    negocio = serializers.PrimaryKeyRelatedField(queryset=models.Negocio.objects.all(), write_only=True)
    
    piso = serializers.CharField(max_length=20, write_only=True, required=False)
    numero = serializers.IntegerField(required=False, write_only=True)
    
    tipo_vehiculo = serializers.PrimaryKeyRelatedField(queryset=models.TipoVehiculo.objects.all(), write_only=True)
    
    class Meta:
        model = models.TarifasNegocio
        fields = ('negocio', 'piso', 'numero', 'tipo_vehiculo', 'tiempo', 'valor')