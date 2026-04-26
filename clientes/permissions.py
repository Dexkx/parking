from rest_framework.permissions import BasePermission


def _get_access(method):

    match method:
        case "PUT":
            return { 'tipo_colaborador': '-1' }
        case "PATCH":
            return { 'tipo_colaborador': '-1' }
        case _:
            return {}


class IsCliente(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False

        return user.is_cliente

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


class IsStaffReserva(BasePermission):
    """
    Permite acceso si el usuario es colaborador o dueño en cualquier nivel
    (Franquicia, Negocio o Sede). No requiere parámetros en la URL.
    """

    def has_permission(self, request, view):
        user = request.user

        return (
            user.sedes.activos().exists()
            or user.negocios.activos().exists()
            or user.franquicias.activos().exists()
        )

    def has_object_permission(self, request, view, obj):
        user = request.user

        # El objeto 'obj' es una instancia de Reserva.
        # Verificamos si el usuario tiene poder sobre esta reserva específica.
        return (
            user.is_sede(obj.sede.pk)
            or user.is_negocio(obj.negocio.pk)
            or (
                obj.negocio.franquicia
                and user.is_franquicia(obj.negocio.franquicia.pk)
            )
        )

from rest_framework.permissions import BasePermission, SAFE_METHODS

class JerarquiaPermission(BasePermission):
    """
    Permiso jerárquico que valida el rol (Dueño, Admin, Empleado)
    en Franquicia > Negocio > Sede.
    """

    def has_permission(self, request, view):
        method = request.method
        if method in SAFE_METHODS:
            return True

        user = request.user
        name_url = view.basename
        sede_pk = view.kwargs.get("sede_pk")

        if name_url in ('sede-puestos', 'sede-tarifas'):
            role = user.get_role_in_sede(sede_pk)

            return role in ('-1', '0')

        return True

    def has_object_permission(self, request, view, obj):
        user = request.user
        if user.is_superuser:
            return True

        # Obtener el rol efectivo para el objeto
        role = None
        model_name = obj.__class__.__name__

        match (model_name):
            case "Franquicias" | "ColaboradresFranquicia":
                role = user.get_role_in_franquicia(
                    obj.franquicia.uuid if hasattr(obj, "franquicia") else obj.uuid
                )

            case "Negocio" | "ColaboradoresNegocio" | "ClienteNegocio":
                role = user.get_role_in_negocio(
                    obj.negocio.nit if hasattr(obj, "negocio") else obj.nit
                )

            case "Sede" | "ColaboradoresSede" | "Puestos" | "Tarifas":
                role = user.get_role_in_sede(
                    obj.sede.uuid if hasattr(obj, "sede") else obj.uuid
                )

        if role is None:
            return False

        # REGLAS DE ACCESO:
        method = request.method
        if method in SAFE_METHODS:
            return True

        print(method, role, model_name)
        match role:
            case "-1":
                return True

            case "0":
                if model_name in ("ColaboradresFranquicia", "ColaboradoresNegocio", "ColaboradoresSede"):
                    return method in ("CREATE", "DELETE")

                if model_name in ("Puestos", "Tarifas", "ClienteNegocio"):
                    return True

            case "1":
                if model_name == "ClienteNegocio":
                    return method in ("CREATE", "DELETE", "PATCH")

            case _:
                return False

        return False
