from django.urls import path, include
from .utils import urlpatterns as utils_urlpatterns
from .usuarios import urlpatterns as usuarios_urlpatterns
from .world import urlpatterns as world_urlpatterns

urlpatterns = [
    path('', include(utils_urlpatterns)),
    path('', include(usuarios_urlpatterns)),
    path('', include(world_urlpatterns)),
]
