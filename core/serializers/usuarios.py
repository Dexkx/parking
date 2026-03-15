from django.contrib.auth.hashers import make_password
from rest_framework import serializers
from .. import models


class UsuarioSR(serializers.ModelSerializer):
    confirm_password = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True)
    # tipo_id = serializers.PrimaryKeyRelatedField(queryset=models.TipoIdentificacion.objects.all(), required=False)

    def validate(self, attrs):
        if attrs["password"] != attrs["confirm_password"]:
            raise serializers.ValidationError("Las contraseñas no coinciden")
        return attrs
    
    def create(self, validated_data):
        validated_data = self._formatear_valores(validated_data)
        return super().create(validated_data)
        
    def update(self, instance, validated_data):
        validated_data = self._formatear_valores(validated_data)
        return super().update(instance, validated_data)
    
    def _formatear_valores(self, validated_data):
        validated_data.pop("confirm_password")
        
        if validated_data.get("password"):
            validated_data['password'] = make_password(validated_data["password"])
            
        if not isinstance(validated_data['tipo_id'], models.TipoIdentificacion):
            validated_data['tipo_id'] = models.TipoIdentificacion.objects.get(pk=validated_data['tipo_id'])
        
        return validated_data

    class Meta:
        model = models.Usuarios
        fields = ("numero_id", "tipo_id", "nombre", "password", "confirm_password")
