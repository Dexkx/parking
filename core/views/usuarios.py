from .. import models
from rest_framework.viewsets import ModelViewSet
from .. import serializers
from rest_framework.permissions import AllowAny, IsAuthenticated
from .mixins import NestedRouterModelMixin, NewCreatedModelMixin


class UsuariosViewSet(ModelViewSet):
    queryset = models.Usuarios.objects.all()
    serializer_class = serializers.UsuarioSR

    def get_permissions(self):
        if self.action == "create":
            self.permission_classes = (AllowAny,)
        else:
            self.permission_classes = (IsAuthenticated,)
        return super().get_permissions()


class VehiculoUsuarioViewSet(NestedRouterModelMixin, NewCreatedModelMixin, ModelViewSet):
    """
    Vehículos registrados de un usuario.
    URL: /usuarios/{numero_id}/vehiculos/
    El usuario puede registrar sus placas para hacer reservas más rápido.
    """
    queryset = models.VehiculosUsuario.objects.all()
    serializer_class = serializers.VehiculoUsuarioSR
    permission_classes = (IsAuthenticated,)
    nested_instances = [
        {
            'lookup': 'usuario',
            'field_name': 'usuario_id',
            'model_class': models.Usuarios,
        }
    ]
