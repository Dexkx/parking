from django.db.models.signals import post_save
from .. import models
from django.dispatch import receiver
from core.models import TipoColaborador

@receiver(post_save, sender=models.Franquicias)
def crear_actualizar_dueno_franquicia(sender, instance, created, **kwargs):
    # Sincroniza el dueño con la tabla de colaboradores (tipo '-1')
    models.ColaboradresFranquicia.objects.update_or_create(
        franquicia=instance,
        tipo_colaborador=TipoColaborador.objects.get(pk='-1'),
        defaults={'usuario': instance.creado_por}
    )
