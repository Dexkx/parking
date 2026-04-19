from rest_framework.permissions import BasePermission

class IsCliente(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False

        return user.is_cliente

class IsNegocio(BasePermission):
    def has_permission(self, request, view):
        # Para obtener los parámetros de la URL (ej: /negocios/123/...)
        # DRF los guarda en view.kwargs
        user = request.user
        if not user.is_authenticated:
            return False

        negocio_id = view.kwargs.get('negocio_pk')
        return user.is_negocio(negocio_id) or user.is_dueno_negocio(negocio_id)

class IsSede(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False

        sede_id = view.kwargs.get('pk')

        return user.is_sede(sede_id) or user.is_dueno_sede(sede_id)

class IsMaster(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False

        return user.is_master

class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False

        return user.is_admin

