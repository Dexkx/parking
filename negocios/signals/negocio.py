from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from .. import models
from core.models import Status

@receiver(post_save, sender=models.Negocio)
def asegurar_puesto_nuevo_dueno_negocio(sender, instance, created, **kwargs):
    models.ColaboradoresNegocio.objects.update_or_create(
        negocio=instance,
        usuario=instance.creado_por,
        tipo_colaborador=models.TipoColaborador.objects.get(pk="-1"),
        defaults={
            "status": Status.objects.get(pk='Activo'),
        }
    )

@receiver(pre_save, sender=models.Negocio)
def actualizar_colaborador_negocio(sender, instance, **kwargs):
    (
        instance.colaboradores.filter(
            usuario=instance.creado_por,
        ).update(
            status=Status.objects.get(pk='Inactivo')
        )
    )
    
@receiver(post_save, sender=models.ColaboradoresNegocio)
@receiver(post_delete, sender=models.ColaboradoresNegocio)
def limpiar_cache_negocio(sender, instance, **kwargs):
    delattr(instance.usuario, 'is_negocio')
            
    
@receiver(post_save, sender=models.TarifasNegocio)
@receiver(post_delete, sender=models.TarifasNegocio)
def limpiar_cache_tarifas_puestos(sender, instance, **kwargs):
    if instance.puesto_negocio is not None:
        delattr(instance.puesto_negocio, 'tarifas')
        return

    if instance.piso is not None:
        puestos = (
            models.PuestoNegocio.objects
            .filter(
                negocio=instance.negocio,
                piso=instance.piso,
                tipo_vehiculo=instance.tipo_vehiculo,
            )
        )
        
        for puesto in puestos:
            delattr(puesto, 'tarifas')
        return
    
    puestos = (
        models.PuestoNegocio.objects
        .filter(
            negocio=instance.negocio,
            tipo_vehiculo=instance.tipo_vehiculo,
        ).activos()
    )
    
    for puesto in puestos:
        delattr(puesto, 'tarifas')