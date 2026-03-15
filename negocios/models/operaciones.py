from core.models import TipoVehiculo
from django.contrib.postgres.constraints import ExclusionConstraint
from django.contrib.postgres.fields import RangeOperators
from django.db.models import Func
import uuid
from psqlextra.models import PostgresPartitionedModel
from psqlextra.types import PostgresPartitioningMethod
from django.db import models
from core.models import ModelCore, Usuarios, VehiculosUsuario
from clientes.models.clientes import ClienteNegocio
from .negocio import Negocio, PuestoNegocio, TarifasNegocio
from django.core.validators import MinValueValidator, MaxValueValidator

class Resena(ModelCore):
    pk = models.CompositePrimaryKey('negocio_id', 'uuid')
    negocio = models.ForeignKey(Negocio, related_name='resenas', on_delete=models.DO_NOTHING)
    uuid = models.UUIDField(editable=False, default=uuid.uuid4, unique=True)
    usuario = models.ForeignKey(Usuarios, related_name='resenas', on_delete=models.PROTECT)
    texto = models.TextField(db_comment='Descripcion de la reseña')
    puntuacion = models.DecimalField(max_digits=4, decimal_places=1, validators=(MinValueValidator(1.0), MaxValueValidator(5.0)))
    
    cliente = models.ForeignObject(
        ClienteNegocio,
        from_fields=('negocio_id', 'usuario_id'),
        to_fields=('negocio_id', 'usuario_id'),
        on_delete=models.DO_NOTHING,
        related_name='resenas',
        null=True,
        blank=True,
    )

    class Meta:
        db_table = 'resenas_negocio'

class Reserva(PostgresPartitionedModel, ModelCore):
    pk = models.CompositePrimaryKey('negocio_id', 'uuid')
    uuid = models.UUIDField(editable=False, default=uuid.uuid4, unique=True)
    
    negocio = models.ForeignKey(Negocio, related_name='reservas', on_delete=models.DO_NOTHING)
    piso = models.CharField(max_length=20, db_comment='piso donde se encuentra el puesto')
    numero = models.IntegerField(validators=(MinValueValidator(1),))
    tipo_vehiculo = models.ForeignKey(TipoVehiculo, on_delete=models.PROTECT)
    tiempo = models.DurationField(db_comment='Tiempo de la tarifa')
    
    usuario = models.ForeignKey(Usuarios, related_name='reservas', on_delete=models.PROTECT)
    placa = models.CharField(max_length=10, db_comment='Placa del vehiculo')
    
    hf_inicio = models.DateTimeField(db_comment='Fecha y hora de inicio de la reserva')
    hf_final = models.DateTimeField(db_comment='Fecha y hora de fin de la reserva')
    
    valor_pagado = models.DecimalField(max_digits=10, decimal_places=2, blank=True, default=0, validators=(MinValueValidator(0),), db_comment='Valor total pagado de la reserva')
    valor_transferencia = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, validators=(MinValueValidator(0),), db_comment='Valor pagado por transferencia')
    valor_tarjeta = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, validators=(MinValueValidator(0),), db_comment='Valor pagado por tarjeta')
    valor_efectivo = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, validators=(MinValueValidator(0),), db_comment='Valor pagado en efectivo')
    
    puesto = models.ForeignObject(
        PuestoNegocio,
        from_fields=('negocio_id', 'piso', 'numero', 'tipo_vehiculo_id'),
        to_fields=('negocio_id', 'piso', 'numero', 'tipo_vehiculo_id'),
        on_delete=models.DO_NOTHING,
        related_name='reservas'
    )
    
    tarifa = models.ForeignObject(
        TarifasNegocio,
        from_fields=('negocio_id', 'tipo_vehiculo_id', 'tiempo'),
        to_fields=('negocio_id', 'tipo_vehiculo_id', 'tiempo'),
        on_delete=models.DO_NOTHING,
        related_name='reservas'
    )
    
    vehiculo = models.ForeignObject(
        VehiculosUsuario,
        from_fields=('usuario_id', 'placa'),
        to_fields=('usuario_id', 'placa'),
        on_delete=models.DO_NOTHING,
        related_name='reservas'
    )
    
    cliente = models.ForeignObject(
        ClienteNegocio,
        from_fields=('negocio_id', 'usuario_id'),
        to_fields=('negocio_id', 'usuario_id'),
        on_delete=models.DO_NOTHING,
        related_name='reservas',
        null=True,
        blank=True,
    )

    class PartitioningMeta:
        method = PostgresPartitioningMethod.RANGE
        key = ("hf_inicio",)

    class Meta:
        db_table = 'reservas_negocio'

        constraints = (
            ExclusionConstraint(
                name='prevenir_superposicion_reservas',
                expressions=(
                    ('negocio', RangeOperators.EQUAL),
                    ('piso', RangeOperators.EQUAL),
                    ('numero', RangeOperators.EQUAL),
                    (Func('hf_inicio', 'hf_final', function='tstzrange'), RangeOperators.OVERLAPS),
                ),
            ),
        )

