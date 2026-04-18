from rest_framework import serializers
from .. import models


class CountrySR(serializers.ModelSerializer):

    class Meta:
        model = models.Countries
        fields = ("id", "name", "iso2", "iso3")


class StateSR(serializers.ModelSerializer):

    class Meta:
        model = models.States
        fields = ("id", "name", "iso2")


class CitySR(serializers.ModelSerializer):

    class Meta:
        model = models.Cities
        fields = ("id", "name",)
