from rest_framework import serializers
from .. import models
from core.serializers import StatusSRMixin, UsuarioSR, TipoColaboradorSR

class FranquiciasSR(StatusSRMixin, serializers.ModelSerializer):
    uuid = serializers.UUIDField(read_only=True)
    
    nit = serializers.CharField(max_length=20, write_only=True)
    numero_verificacion = serializers.IntegerField(write_only=True)
    razon_social = serializers.CharField(max_length=225, write_only=True)
    
    class Meta:
        model = models.Franquicias
        fields = ('uuid', 'nit', 'numero_verificacion', 'razon_social', 'nombre')

class ColaboradoresFranquiciaSR(StatusSRMixin, serializers.ModelSerializer):
    franquicia = serializers.PrimaryKeyRelatedField(queryset=models.Franquicias.objects.all(), write_only=True)
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        
        data['usuario'] = UsuarioSR(instance.usuario).data
        data['tipo_colaborador'] = TipoColaboradorSR(instance.tipo_colaborador).data
        
        return data
    
    class Meta:
        model = models.ColaboradresFranquicia
        fields = ('franquicia', 'usuario', 'tipo_colaborador')

