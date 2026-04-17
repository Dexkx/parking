from django.utils.functional import cached_property
from django.core.validators import MinValueValidator
from django.db import models
from core.models import (
    ModelCore,
    Usuarios,
    Ciudad,
    Departamento,
    Pais,
    TipoVehiculo,
    TipoColaborador,
)
import uuid


class Negocio(ModelCore):
    nit = models.CharField(max_length=20, primary_key=True)
    numero_verificacion = models.IntegerField(validators=(MinValueValidator(1),))
    razon_social = models.CharField(max_length=225)
    nombre = models.CharField(max_length=120, db_comment="nombre para mostrar en la app")
    creado_por = models.ForeignKey(Usuarios, on_delete=models.PROTECT)

    class Meta:
        db_table = "negocios"
        constraints = (
            models.UniqueConstraint(
                name="unico_codigo_verf_negocio", fields=("nit", "numero_verificacion")
            ),
        )

    @property
    def puntuacion(self):
        resenas = self.resenas.all()
        if not resenas.exists():
            return 0.0
        return resenas.aggregate(puntuacion=models.Avg("puntuacion"))["puntuacion"]


class Sede(ModelCore):
    """
    Ubicación física de un parqueadero.
    Jerarquía: Franquicia → Negocio → Sede → Piso → Puesto

    Un negocio puede tener múltiples sedes (ej: Parking S.A. con
    locales en el norte, sur y centro de la ciudad).
    """
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    negocio = models.ForeignKey(
        Negocio, related_name='sedes', on_delete=models.DO_NOTHING,
        db_comment="Negocio al que pertenece esta sede"
    )
    nombre = models.CharField(max_length=120, db_comment="Nombre de la sede (ej: Sede Norte)")
    direccion = models.TextField(db_comment="Dirección física")
    pais = models.ForeignKey(Pais, on_delete=models.PROTECT)
    departamento = models.ForeignKey(Departamento, on_delete=models.PROTECT)
    ciudad = models.ForeignKey(Ciudad, on_delete=models.PROTECT)
    # Coordenadas para el mapa
    lat = models.DecimalField(
        max_digits=10, decimal_places=7,
        null=True, blank=True, db_comment="Latitud GPS"
    )
    lng = models.DecimalField(
        max_digits=10, decimal_places=7,
        null=True, blank=True, db_comment="Longitud GPS"
    )

    class Meta:
        db_table = "sedes"

    @property
    def puntuacion(self):
        """Puntuación promedio de las reseñas de esta sede."""
        resenas = self.resenas.all()
        if not resenas.exists():
            return 0.0
        return resenas.aggregate(p=models.Avg("puntuacion"))["p"]

    def __str__(self):
        return f"{self.negocio.nombre} — {self.nombre}"


class ColaboradoresNegocio(ModelCore):
    pk = models.CompositePrimaryKey("negocio_id", "usuario_id")
    negocio = models.ForeignKey(
        Negocio, related_name="colaboradores", on_delete=models.DO_NOTHING
    )
    usuario = models.ForeignKey(
        Usuarios, related_name="negocios", on_delete=models.DO_NOTHING
    )
    tipo_colaborador = models.ForeignKey(TipoColaborador, on_delete=models.PROTECT)

    class Meta:
        db_table = "colaboradores_negocio"


class PuestoNegocio(ModelCore):
    """
    Puesto de parqueo dentro de una sede.
    La PK compuesta garantiza que no haya dos puestos
    con el mismo piso/número/tipo_vehículo en la misma sede.
    """
    pk = models.CompositePrimaryKey("sede_id", "piso", "numero", "tipo_vehiculo_id")
    sede = models.ForeignKey(
        Sede, related_name="puestos", on_delete=models.DO_NOTHING,
        db_comment="Sede donde está el puesto"
    )
    piso = models.CharField(max_length=20, db_comment="Piso (ej: '1', 'B1', 'Sótano')")
    numero = models.IntegerField(validators=(MinValueValidator(1),), db_comment="Número del puesto")
    tipo_vehiculo = models.ForeignKey(TipoVehiculo, on_delete=models.PROTECT)

    class Meta:
        db_table = "puestos_negocio"

    @cached_property
    def tarifas(self):
        """
        Busca la tarifa aplicable en orden de especificidad:
        1. Tarifa para este puesto específico
        2. Tarifa para el piso de esta sede
        3. Tarifa general de la sede
        """
        # 1. Tarifa específica del puesto
        t = TarifasNegocio.objects.filter(
            sede=self.sede, piso=self.piso,
            numero=self.numero, tipo_vehiculo=self.tipo_vehiculo
        ).activos()
        if t.exists():
            return t

        # 2. Tarifa del piso
        t = TarifasNegocio.objects.filter(
            sede=self.sede, piso=self.piso,
            tipo_vehiculo=self.tipo_vehiculo, numero__isnull=True
        ).activos()
        if t.exists():
            return t

        # 3. Tarifa general de la sede
        return TarifasNegocio.objects.filter(
            sede=self.sede,
            tipo_vehiculo=self.tipo_vehiculo,
            piso__isnull=True, numero__isnull=True
        ).activos()


class TarifasNegocio(ModelCore):
    """
    Tarifa de un puesto en una sede.
    Puede ser:
    - General de la sede (piso=None, numero=None)
    - Por piso (numero=None)
    - Por puesto específico (piso + numero definidos)
    """
    pk = models.CompositePrimaryKey("sede_id", "tipo_vehiculo_id", "tiempo")
    sede = models.ForeignKey(
        Sede, related_name="tarifas", on_delete=models.DO_NOTHING
    )
    piso = models.CharField(
        max_length=20, null=True, blank=True,
        db_comment="Piso específico (null = aplica a toda la sede)"
    )
    numero = models.IntegerField(
        validators=(MinValueValidator(1),), null=True, blank=True,
        db_comment="Número de puesto específico (null = aplica al piso)"
    )
    tipo_vehiculo = models.ForeignKey(TipoVehiculo, on_delete=models.PROTECT)
    tiempo = models.DurationField(db_comment="Fracción de tiempo (ej: 1h, 30min)")
    valor = models.DecimalField(
        max_digits=10, decimal_places=2,
        validators=(MinValueValidator(0),),
        db_comment="Valor en COP"
    )

    puesto = models.ForeignObject(
        PuestoNegocio,
        from_fields=("sede_id", "piso", "numero", "tipo_vehiculo_id"),
        to_fields=("sede_id", "piso", "numero", "tipo_vehiculo_id"),
        on_delete=models.DO_NOTHING,
        related_name="tarifas_puesto",
        null=True, blank=True,
    )

    class Meta:
        db_table = "tarifas_negocio"
