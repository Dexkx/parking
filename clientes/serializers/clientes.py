from rest_framework import serializers
from core.serializers import StatusSRMixin, UsuarioSR
from core.models import Usuarios
from .. import models
from negocios.models import Negocio
from negocios.serializers import NegocioSR


class ClienteNegocioSR(StatusSRMixin, serializers.ModelSerializer):
    """
    Serializer para la relación cliente-negocio.
    Maneja clientes registrados con membresía mensual.
    """
    negocio = serializers.PrimaryKeyRelatedField(
        queryset=Negocio.objects.all()
    )

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['usuario'] = UsuarioSR(instance.usuario).data
        data['negocio'] = NegocioSR(instance.negocio).data
        return data

    class Meta:
        model = models.ClienteNegocio
        fields = ('negocio', 'usuario')
