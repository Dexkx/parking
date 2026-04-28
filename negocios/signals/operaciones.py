from core.models import Status
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from .. import models
from django.utils import timezone


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


@receiver(pre_save, sender=models.Reserva)
def calcular_precio_reserva(sender, instance, **kwargs):
    """
    Calcula hf_fin, tiempo y valor_total basándose en las tarifas del puesto
    cuando la reserva se marca como completada.
    """
    # Solo calculamos si se marca como completado y aún no tiene hf_fin (para no repetir)
    if not instance.is_completado:
        return

    ahora = timezone.now()
    instance.hf_final = ahora

    # 1. Calcular duración total
    duracion = ahora - instance.hf_inicio
    instance.tiempo = duracion

    # 2. Obtener tarifas aplicables al puesto (ordenadas de mayor a menor tiempo)
    tiempo_restante = duracion
    tarifas = (
        instance.puesto
        .tarifas(only_activos=True)
        .filter(
            tiempo__lte=tiempo_restante
        )
        .order_by("-tiempo")
    )

    if not tarifas.exists():
        return

    total_valor = 0
    # 3. Algoritmo Greedy: usar primero las tarifas de mayor duración
    for t in tarifas:
        if tiempo_restante.total_seconds() < t.tiempo.total_seconds():
            continue

        cantidad = int(
            tiempo_restante.total_seconds() // t.tiempo.total_seconds()
        )
        total_valor += cantidad * t.valor
        tiempo_restante -= cantidad * t.tiempo

    # 4. Cobrar fracción: si sobra tiempo más allá del margen de cortesía,
    # sumamos una unidad de la tarifa más pequeña.
    minutos_gracia = instance.minutos_gracia
    if tiempo_restante.total_seconds() > (60 * minutos_gracia):
        # La tarifa más pequeña es la última de la lista (ordenada desc)
        total_valor += tarifas.last().valor

    # Caso especial: si el tiempo total era menor a la tarifa más pequeña
    # pero mayor a la gracia, cobrar la mínima.
    if total_valor == 0 and duracion.total_seconds() > (60 * minutos_gracia):
        total_valor = tarifas.last().valor

    instance.valor_total = total_valor

