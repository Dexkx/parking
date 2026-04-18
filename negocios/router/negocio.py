from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested.routers import NestedDefaultRouter
from .. import views

router = DefaultRouter(trailing_slash=False)
router.register('negocios',    views.NegocioViewSet,    basename='negocios')

# ── /negocios/{nit}/... ──────────────────────────────────────────
negocios_router = NestedDefaultRouter(router, 'negocios', lookup='negocio', trailing_slash=False)
negocios_router.register('colaboradores', views.ColaboradoresNegocioViewSet, basename='negocio-colaboradores')
negocios_router.register('sedes',         views.SedeViewSet,                 basename='negocio-sedes')
negocios_router.register('resenas',       views.ResenaViewSet,               basename='negocio-resenas')
negocios_router.register('reservas',      views.ReservaViewSet,              basename='negocio-reservas')

# ── /negocios/{nit}/sedes/{uuid}/... ────────────────────────────
sedes_router = NestedDefaultRouter(negocios_router, 'sedes', lookup='sede', trailing_slash=False)
sedes_router.register('puestos', views.PuestoNegocioViewSet,   basename='sede-puestos')
sedes_router.register('tarifas', views.TarifasNegocioViewSet,  basename='sede-tarifas')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(negocios_router.urls)),
    path('', include(sedes_router.urls)),
]

