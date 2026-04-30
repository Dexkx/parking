from core.models import ModelCore, Usuarios
from django.db import models

class ClienteNegocio(ModelCore):
    pk = models.CompositePrimaryKey('negocio_id', 'usuario_id')
    negocio = models.ForeignKey('negocios.Negocio', related_name='clientes', on_delete=models.DO_NOTHING)
    usuario = models.ForeignKey(Usuarios, related_name='cliente_negocio', on_delete=models.PROTECT)

    class Meta:
        db_table = 'clientes_negocio'
