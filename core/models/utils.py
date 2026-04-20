from django.core.validators import MinValueValidator
from .core import ModelCore, ModelCoreType
from django.db import models


class TipoVehiculo(ModelCoreType):
    descripcion = False
    value = False

    name = models.CharField(max_length=100, db_comment="Nombre")

    class Meta:
        db_table = "tipos_vehiculos"


class TipoIdentificacion(ModelCoreType):
    name = None
    value = models.CharField(max_length=5, primary_key=True, db_comment="Valor")

    class Meta:
        db_table = "tipos_identificacion"


class TipoColaborador(ModelCoreType):
    value = None
    name = None
    code = models.CharField(max_length=100, primary_key=True, db_comment="Código")

    class Meta:
        db_table = "tipos_colaborador"

