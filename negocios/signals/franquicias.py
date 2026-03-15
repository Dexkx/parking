from django.db.models.signals import post_save, post_delete
from .. import models

@receiver(post_save, sender=models.ColaboradresFranquicia)
@receiver(post_delete, sender=models.ColaboradresFranquicia)
def limpiar_cache_franquicia(sender, instance, **kwargs):
    delattr(instance.usuario, 'is_franquicia')

