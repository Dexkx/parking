from rest_framework import serializers
from .. import models
from core.serializers import StatusSRMixin, UsuarioSR, TipoColaboradorSR, EmptyStringAsNullMixin
from core.models import Usuarios


class FranquiciasSR(EmptyStringAsNullMixin, StatusSRMixin, serializers.ModelSerializer):
    uuid = serializers.UUIDField(read_only=True)

    nit = serializers.CharField(max_length=20, required=False, allow_null=True)
    numero_verificacion = serializers.IntegerField(required=False, allow_null=True)
    razon_social = serializers.CharField(max_length=225, required=False, allow_null=True)

    creado_por = serializers.PrimaryKeyRelatedField(
        queryset=Usuarios.objects.all(), write_only=True
    )

    class Meta:
        model = models.Franquicias
        fields = ('uuid', 'nit', 'numero_verificacion', 'razon_social', 'nombre', 'creado_por', 'status')


class ColaboradoresFranquiciaSR(StatusSRMixin, serializers.ModelSerializer):
    franquicia = serializers.PrimaryKeyRelatedField(
        queryset=models.Franquicias.objects.all(), write_only=True
    )

    status = serializers.BooleanField(required=False)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['usuario'] = UsuarioSR(instance.usuario).data
        data['tipo_colaborador'] = TipoColaboradorSR(instance.tipo_colaborador).data
        return data

    def validate(self, attrs):
        user = attrs.get('usuario')
        franquicia = attrs.get('franquicia')

        if franquicia.is_owner(user):
            raise serializers.ValidationError("El dueño no puede agregarse como colaborador")

        return super().validate(attrs)

    class Meta:
        model = models.ColaboradresFranquicia
        fields = ('franquicia', 'usuario', 'tipo_colaborador', 'status')


class NegociosFranquiciaSR(StatusSRMixin, serializers.ModelSerializer):
    franquicia = serializers.PrimaryKeyRelatedField(
        queryset=models.Franquicias.objects.all(), write_only=True
    )
    negocio = serializers.PrimaryKeyRelatedField(
        queryset=models.Negocio.objects.all(), write_only=True
    )

    def to_representation(self, instance):
        from negocios.serializers.negocios import NegocioSR
        data = super().to_representation(instance)
        data['negocio'] = NegocioSR(instance.negocio).data
        return data

    class Meta:
        model = models.NegociosFranquicia
        fields = ('franquicia', 'negocio')
