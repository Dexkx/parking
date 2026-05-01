from rest_framework import serializers
from ..models import Status
from drf_spectacular.utils import extend_schema_field

class StatusSR(serializers.ModelSerializer):
    """
    Serializer simple para el modelo Status.
    Retorna la representación legible (name) y el valor interno (value).
    """
    class Meta:
        model = Status
        fields = ("name", "value")

class StatusSRMixin:
    """
    Mixin para inyectar un campo 'status' en los serializadores.
    Maneja automáticamente la escritura como PrimaryKey y la lectura con el serializer StatusSR.
    """
    status = serializers.PrimaryKeyRelatedField(
        queryset=Status.objects.all(), required=False
    )

    def get_field_names(self, declared_fields, info):
        fields = super().get_field_names(declared_fields, info)

        fields = list(fields)
        if "status" not in fields:
            fields.append("status")
        return fields

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["status"] = StatusSR(instance.status).data
        return data

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

class CompositePKMixin:
    """
    Mixin para serializadores cuyos modelos utilizan una Primary Key compuesta (CompositePrimaryKey).
    Genera automáticamente un campo 'id' que es la unión de los componentes de la PK.
    """
    id = serializers.SerializerMethodField(read_only=True)

    @extend_schema_field(serializers.CharField())
    def get_id(self, obj):
        """
        Retorna el ID compuesto como un string unido por guiones.
        Si la PK es una tupla (Composite PK), une sus elementos.
        """
        pk = obj.pk
        if isinstance(pk, (list, tuple)):
            return "-".join(str(v) for v in pk if v is not None)
        return str(pk)

    def get_field_names(self, declared_fields, info):
        """
        Asegura que 'id' esté presente en los campos del serializador de forma automática.
        """
        fields = super().get_field_names(declared_fields, info)
        fields = list(fields)
        if "pk" not in fields:
            fields.insert(0, "pk")
        return fields
