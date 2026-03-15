from rest_framework.permissions import BasePermission

class IsCliente(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_cliente
    
class IsNegocio(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_negocio
    
class IsMaster(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_master
    
class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_admin

