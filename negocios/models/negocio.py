from django.utils.functional import cached_property
from django.core.validators import MinValueValidator
from django.db import models
from core.models import (
    ModelCore,
    Usuarios,
    TipoColaborador,
)
from .franquicias import Franquicias


class Negocio(ModelCore):
    nit = models.CharField(max_length=20, primary_key=True)
    numero_verificacion = models.IntegerField(validators=(MinValueValidator(1),))
    razon_social = models.CharField(max_length=225)
    nombre = models.CharField(
        max_length=120, db_comment="nombre para mostrar en la app"
    )
    franquicia = models.ForeignKey(
        Franquicias, related_name="negocios", on_delete=models.PROTECT,
        null=True,
        blank=True,
        default=None,
    )
    creado_por = models.ForeignKey(Usuarios, related_name="dueno_negocios", on_delete=models.PROTECT)

    class Meta:
        db_table = "negocios"
        constraints = (
            models.UniqueConstraint(
                name="unico_codigo_verf_negocio", fields=("nit", "numero_verificacion")
            ),
        )

    @cached_property
    def puntuacion(self):
        return self.resenas.aggregate(p=models.Avg("puntuacion"))["p"] or 0.0

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

        constraints = [
            models.UniqueConstraint(
                condition=models.Q(tipo_colaborador='-1'),
                fields=('negocio', 'tipo_colaborador'),
                name='unico_dueno_negocio'
            )
        ]
