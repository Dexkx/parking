from rest_framework import serializers
from core.serializers import StatusSRMixin, UsuarioSR
from core.models import Usuarios
from ..models import ClienteNegocio


class ClienteNegocioSR(StatusSRMixin, serializers.ModelSerializer):
    """
    Serializer para la relación cliente-negocio.
    Maneja clientes registrados con membresía mensual.
    """
    negocio = serializers.PrimaryKeyRelatedField(write_only=True, read_only=False,
        queryset=__import__('negocios.models', fromlist=['Negocio']).Negocio.objects.all()
    )

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['usuario'] = UsuarioSR(instance.usuario).data
        return data

    class Meta:
        model = ClienteNegocio
        fields = ('negocio', 'usuario')
