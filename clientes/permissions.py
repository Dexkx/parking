from rest_framework.permissions import BasePermission

class IsCliente(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_cliente

class IsNegocio(BasePermission):
    def has_permission(self, request, view):
        # Para obtener los parámetros de la URL (ej: /negocios/123/...)
        # DRF los guarda en view.kwargs
        negocio_id = view.kwargs.get('negocio_pk')
        user = request.user

        return user.is_negocio(negocio_id) or user.is_dueno_negocio(negocio_id)
class IsMaster(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_master

class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_admin

