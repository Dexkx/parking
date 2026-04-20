from django.db.models.signals import post_save
from django.dispatch import receiver
from .. import models
from core.models import TipoColaborador

@receiver(post_save, sender=models.Sede)
def crear_actualizar_dueno_sede(sender, instance, created, **kwargs):
    # Sincroniza el dueño con la tabla de colaboradores de la sede (tipo '-1')
    models.ColaboradoresSede.objects.update_or_create(
        sede=instance,
        tipo_colaborador=TipoColaborador.objects.get(pk='-1'),
        defaults={'usuario': instance.creado_por}
    )
