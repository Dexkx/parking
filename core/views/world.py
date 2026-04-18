from .. import models
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from .. import serializers
from .mixins import NestedRouterModelMixin


class CountryGetOnlyView(RetrieveModelMixin, ListModelMixin, GenericViewSet):
    queryset = models.Countries.objects.all()
    serializer_class = serializers.CountrySR


class StateGetOnlyView(
    RetrieveModelMixin, ListModelMixin, NestedRouterModelMixin, GenericViewSet
):
    queryset = models.States.objects.all()
    serializer_class = serializers.StateSR
    nested_instances = [
        {
            "lookup": "country",
            "field_name": "country",
            "model_class": models.Countries,
        },
    ]


class CityGetOnlyView(
    RetrieveModelMixin, ListModelMixin, NestedRouterModelMixin, GenericViewSet
):
    queryset = models.Cities.objects.all()
    serializer_class = serializers.CitySR
    nested_instances = [
        {
            "lookup": "state",
            "field_name": "state",
            "model_class": models.States,
        },
        {
            "lookup": "country",
            "field_name": "country",
            "model_class": models.Countries,
        },
    ]
