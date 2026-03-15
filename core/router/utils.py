from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested.routers import NestedDefaultRouter
from .. import views 

router = DefaultRouter(trailing_slash=False)
router.register('tipos-vehiculos', views.TipoVehiculoGetOnlyView, basename='tipos-vehiculos')
router.register('tipos-identificacion', views.TipoIdentificacionGetOnlyView, basename='tipos-identificacion')
router.register('tipos-colaborador', views.TipoColaboradorGetOnlyView, basename='tipos-colaborador')
router.register('paises', views.PaisGetOnlyView, basename='paises')

paises_router = NestedDefaultRouter(router, 'paises', lookup='pais', trailing_slash=False)
paises_router.register('departamentos', views.DepartamentoGetOnlyView, basename='departamentos')    
paises_router.register('ciudades', views.CidadGetOnlyView, basename='ciudades')

departamentos_router = NestedDefaultRouter(paises_router, 'departamentos', lookup='departamento', trailing_slash=False)
departamentos_router.register('ciudades', views.CidadGetOnlyView, basename='ciudades')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(paises_router.urls)),
    path('', include(departamentos_router.urls)),
]