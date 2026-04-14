from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested.routers import NestedDefaultRouter
from .. import views

router = DefaultRouter(trailing_slash=False)
router.register('usuarios', views.UsuariosViewSet, basename='usuarios')

# /usuarios/{numero_id}/vehiculos/
usuarios_router = NestedDefaultRouter(router, 'usuarios', lookup='usuario', trailing_slash=False)
usuarios_router.register('vehiculos', views.VehiculoUsuarioViewSet, basename='usuario-vehiculos')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(usuarios_router.urls)),
]
