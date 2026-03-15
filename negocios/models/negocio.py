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


class Negocio(ModelCore):
    nit = models.CharField(max_length=20, primary_key=True)
    numero_verificacion = models.IntegerField(validators=(MinValueValidator(1),))
    razon_social = models.CharField(max_length=225)
    nombre = models.CharField(
        max_length=120, db_comment="nombre para mostrar en la app"
    )
    direccion = models.TextField()
    pais = models.ForeignKey(Pais, on_delete=models.PROTECT)
    departamento = models.ForeignKey(Departamento, on_delete=models.PROTECT)
    ciudad = models.ForeignKey(Ciudad, on_delete=models.PROTECT)
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

        promedio = resenas.aggregate(puntuacion=models.Avg("puntuacion"))["puntuacion"]
        return promedio


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
    pk = models.CompositePrimaryKey("negocio_id", "piso", "numero", "tipo_vehiculo_id")
    negocio = models.ForeignKey(
        Negocio, related_name="puestos", on_delete=models.DO_NOTHING
    )
    piso = models.CharField(
        max_length=20, db_comment="piso donde se encuentra el puesto"
    )
    numero = models.IntegerField(validators=(MinValueValidator(1),))
    tipo_vehiculo = models.ForeignKey(TipoVehiculo, on_delete=models.PROTECT)

    class Meta:
        db_table = "puestos_negocio"
        
    @cached_property
    def tarifas(self):
        if hasattr(self, 'tarifas'):
            tarifas = self.tarifas.objects.activos()
            if tarifas.exists():
                return tarifas
            
        tarifas = (
            TarifasNegocio.objects
            .filter(
                negocio=self.negocio,
                piso=self.piso,
                tipo_vehiculo=self.tipo_vehiculo,
            ).activos()
        )
        if taifas.exists():
            return tarifas
        
        return (
            TarifasNegocio.objects
            .filter(
                negocio=self.negocio,
                tipo_vehiculo=self.tipo_vehiculo,
            ).activos()
        )
                
        

class TarifasNegocio(ModelCore):
    pk = models.CompositePrimaryKey("negocio_id", "tipo_vehiculo_id", "tiempo")
    negocio = models.ForeignKey(
        Negocio, related_name="tarifas", on_delete=models.DO_NOTHING
    )
    piso = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        db_comment="piso donde se encuentra el puesto",
    )
    numero = models.IntegerField(
        validators=(MinValueValidator(1),), null=True, blank=True
    )

    tipo_vehiculo = models.ForeignKey(TipoVehiculo, on_delete=models.PROTECT)
    tiempo = models.DurationField(db_comment="Tiempo de la tarifa")
    valor = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=(MinValueValidator(0),),
        db_comment="Valor de la tarifa",
    )

    puesto_negocio = models.ForeignObject(
        PuestoNegocio,
        from_fields=("negocio_id", "piso", "numero", "tipo_vehiculo_id"),
        to_fields=("negocio_id", "piso", "numero", "tipo_vehiculo_id"),
        on_delete=models.DO_NOTHING,
        related_name="tarifas",
        null=True,
        blank=True,
    )

    class Meta:
        db_table = "tarifas_negocio"
