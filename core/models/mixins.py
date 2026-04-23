from django.db import models
from django.utils.functional import cached_property

class StatusModelMixin(models.Model):
    field_name = 'status'

    @cached_property
    def _get_field_status(self):
        return getattr(self, self.field_name).name or None

    @cached_property
    def is_activo(self):
        return self._get_field_status == 'Activo'

    @cached_property
    def is_inactivo(self):
        return self._get_field_status == 'Inactivo'

    @cached_property
    def is_pendiente(self):
        return self._get_field_status == 'Pendiente'

    @cached_property
    def is_aprobado(self):
        return self._get_field_status == 'Aprobado'

    @cached_property
    def is_rechazado(self):
        return self._get_field_status == 'Rechazado'

    @cached_property
    def is_cancelado(self):
        return self._get_field_status == 'Cancelado'

    @cached_property
    def is_ocupado(self):
        return self._get_field_status == 'Ocupado'

    @cached_property
    def is_libre(self):
        return self._get_field_status == 'Libre'

    @cached_property
    def is_reservado(self):
        return self._get_field_status == 'Reservado'

    @cached_property
    def is_disponible(self):
        return self._get_field_status in ('Activo', 'Libre')

    class Meta:
        abstract = True
