from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers

class DashboardTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        
        if not self.user.is_dashboard_user:
             raise serializers.ValidationError("Este usuario no tiene permisos para acceder al dashboard.")
             
        return data
