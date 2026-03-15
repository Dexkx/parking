from django.core.validators import MinValueValidator
from .core import ModelCore, ModelCoreType
from django.db import models


class TipoVehiculo(ModelCoreType):
    descripcion = False
    value = False
    
    name = models.CharField(max_length=100, db_comment="Nombre")
    llantas = models.IntegerField(
        validators=(MinValueValidator(2),), db_comment="Llantas"
    )

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
    code = models.CharField(max_length=100, db_comment="Código")
    
    class Meta:
        db_table = "tipos_colaborador"

class Pais(ModelCore):
    name = models.CharField(max_length=100, db_comment="Nombre")

    class Meta:
        db_table = "paises"

class Departamento(ModelCore):
    name = models.CharField(max_length=100, db_comment="Nombre")
    pais = models.ForeignKey('Pais', related_name='departamentos', on_delete=models.PROTECT)

    class Meta:
        db_table = "departamentos"

class Ciudad(ModelCore):
    name = models.CharField(max_length=100, db_comment="Nombre")
    pais = models.ForeignKey('Pais', related_name='ciudades', on_delete=models.PROTECT)
    departamento = models.ForeignKey('Departamento', related_name='ciudades', on_delete=models.PROTECT)

    class Meta:
        db_table = "ciudades"
