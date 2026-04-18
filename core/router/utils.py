from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested.routers import NestedDefaultRouter
from .. import views

router = DefaultRouter(trailing_slash=False)
router.register('tipos-vehiculos', views.TipoVehiculoGetOnlyView, basename='tipos-vehiculos')
router.register('tipos-identificacion', views.TipoIdentificacionGetOnlyView, basename='tipos-identificacion')
router.register('tipos-colaborador', views.TipoColaboradorGetOnlyView, basename='tipos-colaborador')



urlpatterns = [
    path('', include(router.urls)),
]
