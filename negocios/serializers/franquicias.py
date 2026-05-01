from rest_framework import serializers
from .. import models
from core.serializers import StatusSRMixin, UsuarioSR, TipoColaboradorSR, EmptyStringAsNullMixin, CompositePKMixin
from core.models import Usuarios


class FranquiciasSR(EmptyStringAsNullMixin, StatusSRMixin, serializers.ModelSerializer):
    """
    Serializer para el modelo Franquicias (Holding).
    Incluye un conteo de los negocios asociados.
    """
    uuid = serializers.UUIDField(read_only=True)

    nit = serializers.CharField(max_length=20, required=False, allow_null=True)
    numero_verificacion = serializers.IntegerField(required=False, allow_null=True)
    razon_social = serializers.CharField(max_length=225, required=False, allow_null=True)

    creado_por = serializers.PrimaryKeyRelatedField(
        queryset=Usuarios.objects.all(), write_only=True
    )

    negocios_count = serializers.SerializerMethodField(read_only=True)
    def get_negocios_count(self, obj) -> int:
        return obj.negocios.count()

    class Meta:
        model = models.Franquicias
        fields = ('uuid', 'nit', 'numero_verificacion', 'razon_social', 'nombre', 'creado_por', 'status', 'negocios_count')


class ColaboradoresFranquiciaSR(CompositePKMixin, StatusSRMixin, serializers.ModelSerializer):
    """
    Serializer para la relación de colaboradores en una franquicia.
    Gestiona la validación para evitar que el dueño sea agregado como colaborador simple.
    """
    franquicia = serializers.PrimaryKeyRelatedField(
        queryset=models.Franquicias.objects.all(), write_only=True
    )
    usuario = serializers.PrimaryKeyRelatedField(
        queryset=Usuarios.objects.all(), required=False
    )

    status = serializers.BooleanField(required=False)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['usuario'] = UsuarioSR(instance.usuario).data
        data['tipo_colaborador'] = TipoColaboradorSR(instance.tipo_colaborador).data
        return data

    def validate(self, attrs):
        franquicia = attrs.get('franquicia')
        if (user := attrs.get('usuario')) and franquicia.is_owner(user):
            raise serializers.ValidationError("El dueño no puede agregarse como colaborador")

        return super().validate(attrs)

    class Meta:
        model = models.ColaboradresFranquicia
        fields = ('franquicia', 'usuario', 'tipo_colaborador', 'status')

