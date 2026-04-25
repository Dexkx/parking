from django.urls import path, include
from .. import views
from .sedes import sedes_router, sedes_publicas_router
from .negocio import negocios_router
from core.router.usuarios import usuarios_router
from rest_framework.routers import DefaultRouter

router = DefaultRouter(trailing_slash=False)
router.register("reservas", views.ReservaAdminViewSet, basename="reservas")

negocios_router.register(
    "tarifas", views.TarifasNegocioViewSet, basename="negocio-tarifas"
)

sedes_publicas_router.register(
    "tarifas", views.TarifasPublicasList, basename="sede-publica-tarifas"
)

sedes_router.register("puestos", views.PuestoSedeViewSet, basename="sede-puestos")
sedes_router.register("tarifas", views.TarifasSedeViewSet, basename="sede-tarifas")
sedes_router.register("resenas", views.ResenaViewSet, basename="negocio-resenas")

usuarios_router.register("reservas", views.ReservasViewSet, basename="reservas")

urlpatterns = [
    path("", include(router.urls)),
    path("", include(negocios_router.urls)),
    path("", include(sedes_router.urls)),
    path("", include(sedes_publicas_router.urls)),
    path("", include(usuarios_router.urls)),
]
