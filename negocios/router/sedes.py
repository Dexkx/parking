from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested.routers import NestedDefaultRouter
from .. import views
from .negocio import negocios_router

router = DefaultRouter(trailing_slash=False)
router.register('sedes', views.SedeViewSet, basename='sede')

# ── /negocios/{nit}/sedes/{uuid}/... ────────────────────────────
sedes_router = NestedDefaultRouter(negocios_router, 'sedes', lookup='sede', trailing_slash=False)
sedes_router.register('puestos', views.PuestoNegocioViewSet,   basename='sede-puestos')
sedes_router.register('tarifas', views.TarifasNegocioViewSet,  basename='sede-tarifas')

urlpatterns = [
    path('', include(sedes_router.urls)),
]
