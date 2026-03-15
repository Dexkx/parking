from config.managers import StatusQuerySet
from django.db import models


class ModelCoreBase(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, db_comment="Fecha de creación")
    updated_at = models.DateTimeField(
        auto_now=True, db_comment="Fecha de actualización"
    )

    class Meta:
        abstract = True


class _ModelCoreType(ModelCoreBase):
    name = models.CharField(max_length=100, db_comment="Nombre")
    descripcion = models.TextField(
        blank=True, null=True, default=None, db_comment="Descripción"
    )
    value = models.TextField(db_comment="Valor")

    class Meta:
        abstract = True


class Status(_ModelCoreType):
    """Modelo para manejar estados"""

    name = models.CharField(max_length=100, primary_key=True, db_comment="Nombre")

    class Meta:
        db_table = "estados"


class ModelCoreType(_ModelCoreType):
    objects = models.Manager.from_queryset(StatusQuerySet)()
    
    status = models.ForeignKey(
        Status,
        on_delete=models.CASCADE,
        db_comment="Estado",
        default="Activo",
        blank=True,
    )

    class Meta:
        abstract = True


class ModelCore(ModelCoreBase):
    objects = models.Manager.from_queryset(StatusQuerySet)()
    
    status = models.ForeignKey(
        Status,
        on_delete=models.CASCADE,
        db_comment="Estado",
        default="Activo",
        blank=True,
    )

    class Meta:
        abstract = True
