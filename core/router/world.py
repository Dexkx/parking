from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested.routers import NestedDefaultRouter
from .. import views

router = DefaultRouter(trailing_slash=False)
router.register('countries', views.CountryGetOnlyView, basename='countries')
paises_router = NestedDefaultRouter(
    router, 'countries', lookup='country', trailing_slash=False
)
paises_router.register('states', views.StateGetOnlyView, basename='states')

departamentos_router = NestedDefaultRouter(
    paises_router, 'states', lookup='state', trailing_slash=False
)
departamentos_router.register('cities', views.CityGetOnlyView, basename='cities')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(paises_router.urls)),
    path('', include(departamentos_router.urls)),
]
