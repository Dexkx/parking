from django.db import models

class StatusQuerySet(models.QuerySet):
    def activos(self):
        return self.filter(status='Activo')

    def inactivos(self):
        return self.filter(status='Inactivo')

    def pendientes(self):
        return self.filter(status='Pendiente')

    def aprobados(self):
        return self.filter(status='Aprobado')

    def rechazados(self):
        return self.filter(status='Rechazado')

    def cancelados(self):
        return self.filter(status='Cancelado')

    def ocupados(self):
        return self.filter(status='Ocupado')

    def libres(self):
        return self.filter(status='Libre')

    def reservados(self):
        return self.filter(status='Reservado')
