from django.core.validators import MinValueValidator
from core.models import ModelCore, Usuarios, TipoColaborador
from django.db import models
import uuid
from .negocio import Negocio

class Franquicias(ModelCore):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    nit = models.CharField(max_length=20, null=True, blank=True)
    numero_verificacion = models.IntegerField(validators=(MinValueValidator(1),), null=True, blank=True)
    razon_social = models.CharField(max_length=225, null=True, blank=True)
    
    nombre = models.CharField(max_length=120, db_comment='nombre para mostrar en la app')
    
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

class ColaboradresFranquicia(ModelCore):
    pk = models.CompositePrimaryKey('franquicia_id', 'usuario_id')
    franquicia = models.ForeignKey(Franquicias, related_name='colaboradores', on_delete=models.DO_NOTHING)
    usuario = models.ForeignKey(Usuarios, related_name='franquicias', on_delete=models.DO_NOTHING)
    tipo_colaborador = models.ForeignKey(TipoColaborador, on_delete=models.PROTECT)
    
    class Meta:
        db_table = 'colaboradores_franquicia'

class NegociosFranquicia(ModelCore):
    pk = models.CompositePrimaryKey('franquicia_id', 'negocio_id')
    franquicia = models.ForeignKey(Franquicias, related_name='negocios', on_delete=models.DO_NOTHING)
    negocio = models.ForeignKey(Negocio, related_name='franquicias', on_delete=models.DO_NOTHING)
    
    class Meta:
        db_table = 'negocios_franquicia'

