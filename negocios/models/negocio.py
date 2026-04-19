from django.utils.functional import cached_property
from django.core.validators import MinValueValidator
from django.db import models
from core.models import (
    ModelCore,
    Usuarios,
    TipoColaborador,
)


class Negocio(ModelCore):
    nit = models.CharField(max_length=20, primary_key=True)
    numero_verificacion = models.IntegerField(validators=(MinValueValidator(1),))
    razon_social = models.CharField(max_length=225)
    nombre = models.CharField(
        max_length=120, db_comment="nombre para mostrar en la app"
    )
    creado_por = models.ForeignKey(Usuarios, related_name="dueno_negocios", on_delete=models.PROTECT)

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

    def is_owner(self, user):
        return self.creado_por == user

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

