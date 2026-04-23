from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested.routers import NestedDefaultRouter
from .. import views

router = DefaultRouter(trailing_slash=False)
router.register('sedes', views.SedeViewSet, basename='sede')
router.register('sedes-publicas', views.SedePublicViewSet, basename='sede-publica')

sedes_publicas_router = NestedDefaultRouter(router, 'sedes-publicas', lookup='sede_publica', trailing_slash=False)
# ── /negocios/{nit}/sedes/{uuid}/... ────────────────────────────
sedes_router = NestedDefaultRouter(router, 'sedes', lookup='sede', trailing_slash=False)
sedes_router.register('colaboradores', views.ColaboradoresSedeViewSet,   basename='sede-colaboradores')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(sedes_router.urls)),
]
