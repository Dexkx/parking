from django.urls import path, include
from .franquicias import urlpatterns as franquicias_router
from .negocio import urlpatterns as negocios_router
from .sedes import urlpatterns as sedes_router

urlpatterns = [
    path('', include(franquicias_router)),
    path('', include(negocios_router)),
    path('', include(sedes_router)),
]
