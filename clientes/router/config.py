from django.urls import path, include
from rest_framework_nested.routers import NestedDefaultRouter
from rest_framework.routers import DefaultRouter
from negocios import views as negocios_views
from clientes.views import ClienteNegocioViewSet

# Reutilizamos el router base de negocios para anidar clientes
# /negocios/{nit}/clientes/
_base_router = DefaultRouter(trailing_slash=False)
_base_router.register('negocios', negocios_views.NegocioViewSet, basename='negocios')

clientes_router = NestedDefaultRouter(_base_router, 'negocios', lookup='negocio', trailing_slash=False)
clientes_router.register('clientes', ClienteNegocioViewSet, basename='negocio-clientes')

urlpatterns = [
    path('', include(clientes_router.urls)),
]
