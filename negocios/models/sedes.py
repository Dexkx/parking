from django.utils.functional import cached_property
from django.core.validators import MinValueValidator
from django.db import models
from core.models import (
    ModelCore,
    Cities,
    States,
    Countries,
    Usuarios,
    TipoColaborador,
)
from .negocio import Negocio
import uuid


class Sede(ModelCore):
    """
    Ubicación física de un parqueadero.
    Jerarquía: Franquicia → Negocio → Sede → Piso → Puesto

    Un negocio puede tener múltiples sedes (ej: Parking S.A. con
    locales en el norte, sur y centro de la ciudad).
    """

    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    negocio = models.ForeignKey(
        Negocio,
        related_name="sedes",
        on_delete=models.DO_NOTHING,
        db_comment="Negocio al que pertenece esta sede",
    )
    nombre = models.CharField(
        max_length=120, db_comment="Nombre de la sede (ej: Sede Norte)"
    )
    direccion = models.TextField(db_comment="Dirección física")
    country = models.ForeignKey(Countries, on_delete=models.PROTECT)
    state = models.ForeignKey(States, on_delete=models.PROTECT)
    city = models.ForeignKey(Cities, null=True, blank=True, on_delete=models.PROTECT)
    # Coordenadas para el mapa
    lat = models.DecimalField(
        max_digits=10, decimal_places=7, null=True, blank=True, db_comment="Latitud GPS"
    )
    lng = models.DecimalField(
        max_digits=10,
        decimal_places=7,
        null=True,
        blank=True,
        db_comment="Longitud GPS",
    )
    creado_por = models.ForeignKey(Usuarios, related_name="dueno_sede", on_delete=models.PROTECT)

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


class ColaboradoresSede(ModelCore):
    pk = models.CompositePrimaryKey("sede_id", "usuario_id")
    sede = models.ForeignKey(
        Sede, related_name="colaboradores", on_delete=models.DO_NOTHING
    )
    usuario = models.ForeignKey(
        Usuarios, related_name="sedes", on_delete=models.DO_NOTHING
    )
    tipo_colaborador = models.ForeignKey(TipoColaborador, on_delete=models.PROTECT)

    class Meta:
        db_table = "colaboradores_sede"
