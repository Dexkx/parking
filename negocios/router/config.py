from django.urls import path, include
from .franquicias import urlpatterns as franquicias_router
from .negocio import urlpatterns as negocios_router

urlpatterns = [
    path('', include(franquicias_router)),
    path('', include(negocios_router)),
]
