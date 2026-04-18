from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested.routers import NestedDefaultRouter
from .. import views

router = DefaultRouter(trailing_slash=False)
router.register('franquicias', views.FranquiciasViewSet, basename='franquicias')

# ── /franquicias/{uuid}/... ──────────────────────────────────────
franquicias_router = NestedDefaultRouter(router, 'franquicias', lookup='franquicia', trailing_slash=False)
franquicias_router.register('colaboradores', views.ColaboradoresFranquiciaViewSet, basename='franquicia-colaboradores')
franquicias_router.register('negocios',      views.NegociosFranquiciaViewSet,      basename='franquicia-negocios')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(franquicias_router.urls)),
]
