from config.managers import StatusQuerySet
from django.db import models
from .mixins import StatusModelMixin
from django.utils.functional import classproperty


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

    @classproperty
    def ACTIVO(cls):
        return cls.objects.get(pk='Activo')

    @classproperty
    def INACTIVO(cls):
        return cls.objects.get(pk='Inactivo')

    @classproperty
    def PENDIENTE(cls):
        return cls.objects.get(pk='Pendiente')

    @classproperty
    def APROBADO(cls):
        return cls.objects.get(pk='Aprobado')

    @classproperty
    def RECHAZADO(cls):
        return cls.objects.get(pk='Rechazado')

    @classproperty
    def CANCELADO(cls):
        return cls.objects.get(pk='Cancelado')

    @classproperty
    def OCUPADO(cls):
        return cls.objects.get(pk='Ocupado')

    @classproperty
    def LIBRE(cls):
        return cls.objects.get(pk='Libre')

    @classproperty
    def RESERVADO(cls):
        return cls.objects.get(pk='Reservado')

    @classproperty
    def COMPLETADO(cls):
        return cls.objects.get(pk='Completado')

    class Meta:
        db_table = "estados"



class ModelCoreType(StatusModelMixin, _ModelCoreType):
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


class ModelCore(StatusModelMixin, ModelCoreBase):
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
