from django.urls import path, include
from .. import views
from .sedes import sedes_router
from .negocio import negocios_router

negocios_router.register("tarifas", views.TarifasNegocioViewSet, basename="negocio-tarifas")

sedes_router.register("puestos", views.PuestoSedeViewSet, basename="sede-puestos")
sedes_router.register("tarifas", views.TarifasSedeViewSet, basename="sede-tarifas")
sedes_router.register("resenas", views.ResenaViewSet, basename="negocio-resenas")
sedes_router.register("reservas", views.ReservaViewSet, basename="negocio-reservas")

urlpatterns = [
    path("", include(negocios_router.urls)),
    path("", include(sedes_router.urls)),
]
