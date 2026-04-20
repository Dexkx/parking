from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested.routers import NestedDefaultRouter
from .. import views

router = DefaultRouter(trailing_slash=False)
router.register("negocios", views.NegocioViewSet, basename="negocios")

# ── /negocios/{nit}/... ──────────────────────────────────────────
negocios_router = NestedDefaultRouter(
    router, "negocios", lookup="negocio", trailing_slash=False
)
negocios_router.register(
    "colaboradores", views.ColaboradoresNegocioViewSet, basename="negocio-colaboradores"
)

urlpatterns = [
    path("", include(router.urls)),
    path("", include(negocios_router.urls)),
]
