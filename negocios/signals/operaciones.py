from django.db.models.signals import pre_save
from django.dispatch import receiver
from .. import models


@receiver(pre_save, sender=models.Reserva)
def actualizar_valor_total_pagado_reserva(sender, instance, **kwargs):
    total_pagado = 0.0

    total_pagado += instance.valor_transferencia or 0.0
    total_pagado += instance.valor_tarjeta or 0.0
    total_pagado += instance.valor_efectivo or 0.0

    instance.valor_pagado = total_pagado

