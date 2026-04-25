from core.models import Status
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from .. import models


@receiver(pre_save, sender=models.Reserva)
def actualizar_valor_total_pagado_reserva(sender, instance, **kwargs):
    total_pagado = 0.0

    total_pagado += instance.valor_transferencia or 0.0
    total_pagado += instance.valor_tarjeta or 0.0
    total_pagado += instance.valor_efectivo or 0.0

    instance.valor_pagado = total_pagado


@receiver(post_save, sender=models.Reserva)
def actualizar_disponibilidad_puesto(sender, instance, **kwargs):
    """
    Actualiza la disponibilidad del puesto basado en el estado de la reserva.
    """
    if instance.is_reservado:
        setattr(instance.puesto, "status", Status.RESERVADO)

    elif instance.is_cancelado or instance.is_completado:
        setattr(instance.puesto, "status", Status.LIBRE)

    elif instance.is_activo:
        setattr(instance.puesto, "status", Status.OCUPADO)

    instance.puesto.save(update_fields=["status"])
