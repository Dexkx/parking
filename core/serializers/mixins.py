from rest_framework import serializers
from ..models import Status


class StatusSRMixin:
    status = serializers.PrimaryKeyRelatedField(
        queryset=Status.objects.all(), required=False
    )

    def get_field_names(self, declared_fields, info):
        fields = super().get_field_names(declared_fields, info)

        fields = list(fields)
        if "status" not in fields:
            fields.append("status")
        return fields

class EmptyStringAsNullMixin:
    """
    Mixin para serializadores que convierte automáticamente strings vacíos ("")
    en None (null) para cualquier campo que tenga definido allow_null=True.
    Muy útil para campos numéricos o de fecha que vienen vacíos desde el frontend.
    """
    def to_internal_value(self, data):
        if not isinstance(data, dict):
            return super().to_internal_value(data)

        data = data.copy()
        for field_name, field in self.fields.items():
            # Si el campo permite nulos y el valor recibido es un string vacío
            if getattr(field, 'allow_null', False) and data.get(field_name) == '':
                data[field_name] = None

        return super().to_internal_value(data)
