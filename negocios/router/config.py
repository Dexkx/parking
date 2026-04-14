from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested.routers import NestedDefaultRouter
from .. import views

router = DefaultRouter(trailing_slash=False)
router.register('negocios', views.NegocioViewSet, basename='negocios')
router.register('franquicias', views.FranquiciasViewSet, basename='franquicias')

# /negocios/{nit}/colaboradores/
# /negocios/{nit}/puestos/
# /negocios/{nit}/tarifas/
# /negocios/{nit}/resenas/
# /negocios/{nit}/reservas/
negocios_router = NestedDefaultRouter(router, 'negocios', lookup='negocio', trailing_slash=False)
negocios_router.register('colaboradores', views.ColaboradoresNegocioViewSet, basename='negocio-colaboradores')
negocios_router.register('puestos', views.PuestoNegocioViewSet, basename='negocio-puestos')
negocios_router.register('tarifas', views.TarifasNegocioViewSet, basename='negocio-tarifas')
negocios_router.register('resenas', views.ResenaViewSet, basename='negocio-resenas')
negocios_router.register('reservas', views.ReservaViewSet, basename='negocio-reservas')

# /franquicias/{uuid}/colaboradores/
# /franquicias/{uuid}/negocios/
franquicias_router = NestedDefaultRouter(router, 'franquicias', lookup='franquicia', trailing_slash=False)
franquicias_router.register('colaboradores', views.ColaboradoresFranquiciaViewSet, basename='franquicia-colaboradores')
franquicias_router.register('negocios', views.NegociosFranquiciaViewSet, basename='franquicia-negocios')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(negocios_router.urls)),
    path('', include(franquicias_router.urls)),
]
