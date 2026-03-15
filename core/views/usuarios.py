from .. import models
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from .. import serializers
from rest_framework.permissions import AllowAny, IsAuthenticated

class UsuariosViewSet(ModelViewSet):
    queryset = models.Usuarios.objects.all()
    serializer_class = serializers.UsuarioSR
    
    
    def get_permissions(self):
        
        if self.action == "create":
            self.permission_classes = (AllowAny,)
        
        else:
            self.permission_classes = (IsAuthenticated,)
        
        return super().get_permissions()

