from django.db.models.signals import post_save
from django.dispatch import receiver
from .. import models
from core.models import TipoColaborador

@receiver(post_save, sender=models.Negocio)
def crear_actualizar_dueno_negocio(sender, instance, created, **kwargs):
    # Esto maneja tanto la creación inicial como el cambio de dueño,
    # y recrea el registro si fue borrado manualmente.
    models.ColaboradoresNegocio.objects.update_or_create(
        negocio=instance,
        tipo_colaborador=TipoColaborador.objects.get(pk='-1'),
        defaults={'usuario': instance.creado_por}
    )
