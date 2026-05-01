from django.core.validators import MinValueValidator
from core.models import ModelCore, Usuarios, TipoColaborador
from django.db import models
import uuid

class Franquicias(ModelCore):
    """
    Modelo que representa una Franquicia (Holding).
    Agrupa múltiples negocios bajo una misma entidad legal o administrativa.
    """
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    nit = models.CharField(max_length=20, null=True, blank=True)
    numero_verificacion = models.IntegerField(validators=(MinValueValidator(1),), null=True, blank=True)
    razon_social = models.CharField(max_length=225, null=True, blank=True)

    nombre = models.CharField(max_length=120, db_comment='nombre para mostrar en la app')
    creado_por = models.ForeignKey(Usuarios, related_name='dueno_franquicias', on_delete=models.PROTECT)

    class Meta:
        db_table = 'franquicias'

        constraints = (
            models.CheckConstraint(
                name='validar_datos_franquicia_completos',
                condition=(
                    models.Q(nit__isnull=True, numero_verificacion__isnull=True, razon_social__isnull=True) |
                    models.Q(nit__isnull=False, numero_verificacion__isnull=False, razon_social__isnull=False)
                )
            ),
        )

    def is_owner(self, user):
        return self.creado_por == user

class ColaboradresFranquicia(ModelCore):
    """
    Relación M2M entre Usuarios y Franquicias con roles específicos.
    Define qué usuarios pueden gestionar una franquicia y con qué nivel de permisos.
    """
    pk = models.CompositePrimaryKey('franquicia_id', 'usuario_id')
    franquicia = models.ForeignKey(Franquicias, related_name='colaboradores', on_delete=models.DO_NOTHING)
    usuario = models.ForeignKey(Usuarios, related_name='franquicias', on_delete=models.DO_NOTHING)
    tipo_colaborador = models.ForeignKey(TipoColaborador, on_delete=models.PROTECT)

    class Meta:
        db_table = 'colaboradores_franquicia'

        constraints = [
            models.UniqueConstraint(
                condition=models.Q(tipo_colaborador='-1'),
                fields=('franquicia', 'tipo_colaborador'),
                name='unico_dueno_franquicia'
            )
        ]


