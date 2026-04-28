from django.contrib.postgres.fields import DateTimeRangeField
from django.db.models import Func, Value

class TsTzRange(Func):
    """Convierte dos DateTimeFields en un rango tstzrange de PostgreSQL."""
    function = "TSTZRANGE"
    output_field = DateTimeRangeField()

    def __init__(self, lower, upper, bounds="[)", **kwargs):
        # El tercer argumento '[)' le dice explícitamente a PG cómo
        # manejar los límites, especialmente cuando upper es NULL → [lower, ∞)
        super().__init__(lower, upper, Value(bounds), **kwargs)
