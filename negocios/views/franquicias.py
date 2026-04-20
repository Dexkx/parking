from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from core.views.mixins import NestedRouterModelMixin, NewCreatedModelMixin
from .. import models
from ..serializers import FranquiciasSR, ColaboradoresFranquiciaSR


class FranquiciasViewSet(ModelViewSet):
    """
    CRUD de franquicias (empresas que agrupan varios parqueaderos).
    Requiere autenticación para todas las operaciones.
    """
    queryset = models.Franquicias.objects.all()
    serializer_class = FranquiciasSR
    permission_classes = (IsAuthenticated,)


class ColaboradoresFranquiciaViewSet(NestedRouterModelMixin, NewCreatedModelMixin, ModelViewSet):
    """
    Gestión de colaboradores de una franquicia.
    URL: /franquicias/{uuid}/colaboradores/
    """
    queryset = models.ColaboradresFranquicia.objects.all()
    serializer_class = ColaboradoresFranquiciaSR
    lookup_field = "usuario"
    permission_classes = (IsAuthenticated,)
    nested_instances = [
        {
            'lookup': 'franquicia',
            'field_name': 'franquicia_id',
            'model_class': models.Franquicias,
        }
    ]
