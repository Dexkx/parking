from django.contrib.postgres.constraints import ExclusionConstraint
from django.contrib.postgres.fields import RangeOperators
from django.db.models import Func
import uuid
from psqlextra.models import PostgresPartitionedModel
from psqlextra.types import PostgresPartitioningMethod
from django.db import models
from core.models import ModelCore, Usuarios, VehiculosUsuario, TipoVehiculo
from clientes.models.clientes import ClienteNegocio
from .negocio import Negocio
from .sedes import Sede
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.functional import cached_property


class Puestos(ModelCore):
    """
    Puesto de parqueo dentro de una sede.
    La PK compuesta garantiza que no haya dos puestos
    con el mismo piso/número/tipo_vehículo en la misma sede.
    """

    pk = models.CompositePrimaryKey("sede_id", "piso", "numero", "tipo_vehiculo")
    sede = models.ForeignKey(
        Sede,
        related_name="puestos",
        on_delete=models.PROTECT,
        db_comment="Sede donde está el puesto",
    )
    piso = models.CharField(max_length=20, db_comment="Piso (ej: '1', 'B1', 'Sótano')")
    numero = models.IntegerField(
        validators=(MinValueValidator(1),), db_comment="Número del puesto"
    )
    tipo_vehiculo = models.ForeignKey(TipoVehiculo, on_delete=models.PROTECT)

    class Meta:
        db_table = "puestos"

    def tarifas(self, only_activos=False):
        """
        Busca la tarifa aplicable en orden de especificidad:
        1. Tarifa para este puesto específico
        2. Tarifa para el piso de esta sede
        3. Tarifa general de la sede
        """
        # 1. Tarifa específica del puesto
        t = self.tarifas_puesto
        t = t.activos() if only_activos else t.all()
        if t.exists():
            return t

        # 2. Tarifa del piso
        t = Tarifas.objects.filter(
            sede=self.sede,
            piso=self.piso,
            tipo_vehiculo=self.tipo_vehiculo,
            numero__isnull=True,
        )
        t = t.activos() if only_activos else t.all()
        if t.exists():
            return t

        # 3. Tarifa general de la sede
        t = self.sede.tarifas.filter(
            tipo_vehiculo=self.tipo_vehiculo,
            piso__isnull=True,
            numero__isnull=True,
        )
        t = t.activos() if only_activos else t.all()
        if t.exists():
            return t

        # 4. Tarifa general del negocio
        t = self.sede.negocio.tarifas.filter(
            sede__isnull=True,
            tipo_vehiculo=self.tipo_vehiculo,
            piso__isnull=True,
            numero__isnull=True,
        )
        return t.activos() if only_activos else t.all()


class Tarifas(ModelCore):
    """
    Tarifa de un puesto en una sede.
    Puede ser:
    - General de la sede (piso=None, numero=None)
    - Por piso (numero=None)
    - Por puesto específico (piso + numero definidos)
    """

    uuid = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    negocio = models.ForeignKey(
        Negocio, related_name="tarifas", on_delete=models.PROTECT
    )
    sede = models.ForeignKey(
        Sede,
        related_name="tarifas",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        default=None,
        db_comment="Sede específica (null = aplica a todo el negocio)",
    )
    piso = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        db_comment="Piso específico (null = aplica a toda la sede)",
    )
    numero = models.IntegerField(
        validators=(MinValueValidator(1),),
        null=True,
        blank=True,
        default=None,
        db_comment="Número de puesto específico (null = aplica al piso)",
    )
    tipo_vehiculo = models.ForeignKey(TipoVehiculo, on_delete=models.PROTECT)
    tiempo = models.DurationField(db_comment="Fracción de tiempo (ej: 1h, 30min)")
    valor = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=(MinValueValidator(0),),
        db_comment="Valor en COP",
    )

    puesto = models.ForeignObject(
        Puestos,
        from_fields=("sede_id", "piso", "numero", "tipo_vehiculo_id"),
        to_fields=("sede_id", "piso", "numero", "tipo_vehiculo_id"),
        on_delete=models.PROTECT,
        related_name="tarifas_puesto",
        null=True,
        blank=True,
    )

    class Meta:
        db_table = "tarifas"


class Resena(ModelCore):
    uuid = models.UUIDField(editable=False, default=uuid.uuid4, primary_key=True)
    negocio = models.ForeignKey(
        Negocio, related_name="resenas", on_delete=models.PROTECT
    )
    sede = models.ForeignKey(Sede, related_name="resenas", on_delete=models.PROTECT)
    usuario = models.ForeignKey(
        Usuarios, related_name="resenas", on_delete=models.PROTECT
    )
    texto = models.TextField(db_comment="Descripcion de la reseña")
    puntuacion = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        validators=(MinValueValidator(1.0), MaxValueValidator(5.0)),
    )

    cliente = models.ForeignObject(
        ClienteNegocio,
        from_fields=("negocio_id", "usuario_id"),
        to_fields=("negocio_id", "usuario_id"),
        on_delete=models.PROTECT,
        related_name="resenas",
        null=True,
        blank=True,
        default=None,
    )

    class Meta:
        db_table = "resenas"


class Reserva(PostgresPartitionedModel, ModelCore):
    uuid = models.UUIDField(editable=False, primary_key=True, default=uuid.uuid4)

    negocio = models.ForeignKey(
        Negocio, related_name="reservas", on_delete=models.PROTECT
    )
    sede = models.ForeignKey(Sede, related_name="reservas", on_delete=models.PROTECT)
    piso = models.CharField(
        max_length=20, db_comment="piso donde se encuentra el puesto"
    )
    numero = models.IntegerField(validators=(MinValueValidator(1),))
    tipo_vehiculo = models.ForeignKey(TipoVehiculo, on_delete=models.PROTECT)
    tiempo = models.DurationField(db_comment="Tiempo de la tarifa")

    usuario = models.ForeignKey(
        Usuarios, related_name="reservas", on_delete=models.PROTECT
    )
    placa = models.CharField(max_length=10, db_comment="Placa del vehiculo")

    tarifa = models.ForeignKey(Tarifas, on_delete=models.PROTECT)

    hf_inicio = models.DateTimeField(db_comment="Fecha y hora de inicio de la reserva")
    hf_final = models.DateTimeField(db_comment="Fecha y hora de fin de la reserva")

    valor_pagado = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        default=0,
        validators=(MinValueValidator(0),),
        db_comment="Valor total pagado de la reserva",
    )
    valor_transferencia = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=(MinValueValidator(0),),
        db_comment="Valor pagado por transferencia",
    )
    valor_tarjeta = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=(MinValueValidator(0),),
        db_comment="Valor pagado por tarjeta",
    )
    valor_efectivo = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=(MinValueValidator(0),),
        db_comment="Valor pagado en efectivo",
    )

    puesto = models.ForeignObject(
        Puestos,
        from_fields=("sede_id", "piso", "numero", "tipo_vehiculo_id"),
        to_fields=("sede_id", "piso", "numero", "tipo_vehiculo_id"),
        on_delete=models.PROTECT,
        related_name="reservas",
    )

    vehiculo = models.ForeignObject(
        VehiculosUsuario,
        from_fields=("usuario_id", "placa"),
        to_fields=("usuario_id", "placa"),
        on_delete=models.PROTECT,
        related_name="reservas",
    )

    cliente = models.ForeignObject(
        ClienteNegocio,
        from_fields=("negocio_id", "usuario_id"),
        to_fields=("negocio_id", "usuario_id"),
        on_delete=models.PROTECT,
        related_name="reservas",
        null=True,
        blank=True,
    )

    class PartitioningMeta:
        method = PostgresPartitioningMethod.RANGE
        key = ("hf_inicio",)

    class Meta:
        db_table = "reservas"

        constraints = (
            ExclusionConstraint(
                name="en",
                expressions=(
                    ("negocio", RangeOperators.EQUAL),
                    ("sede", RangeOperators.EQUAL),
                    ("piso", RangeOperators.EQUAL),
                    ("numero", RangeOperators.EQUAL),
                    (
                        Func("hf_inicio", "hf_final", function="tstzrange"),
                        RangeOperators.OVERLAPS,
                    ),
                ),
            ),
        )
