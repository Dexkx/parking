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

        negocio_id = view.kwargs.get("negocio_pk")
        return user.is_negocio(negocio_id) or user.is_dueno_negocio(negocio_id)


class IsSede(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False

        # Intentamos obtener el ID de la sede desde los kwargs.
        # 'sede_pk' para rutas anidadas, 'pk' para vistas de detalle directas.
        sede_id = view.kwargs.get("sede_pk")
        if not sede_id and getattr(view, "detail", False):
            sede_id = view.kwargs.get("pk")

        # Si no hay un ID de sede involucrado en la URL, omitimos el chequeo.
        if not sede_id:
            return True

        return user.is_sede(sede_id) or user.is_dueno_sede(sede_id)


# class isDuenoReserva(BasePermission):
#     def has_permission(self, request, view):
#         user = request.user
#         if not user.is_authenticated:
#             return False

#         reserva_id = view.kwargs.get('reserva_pk')
#         if not reserva_id and getattr(view, 'detail', False):
#             reserva_id = view.kwargs.get('pk')

#         if not reserva_id:
#             return True

#         return user.is_dueno_reserva(reserva_id)


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
        if not user.is_authenticated:
            return False

        # Verificamos si existe alguna relación de colaboración activa
        return (
            user.sedes.activos().exists()
            or user.negocios.activos().exists()
            or user.franquicias.activos().exists()
            or user.dueno_sedes.activos().exists()
            or user.dueno_negocios.activos().exists()
            or user.dueno_franquicias.activos().exists()
        )

    def has_object_permission(self, request, view, obj):
        user = request.user
        if user.is_superuser:
            return True

        # El objeto 'obj' es una instancia de Reserva.
        # Verificamos si el usuario tiene poder sobre esta reserva específica.
        return (
            user.is_sede(obj.sede.pk)
            or user.is_dueno_sede(obj.sede.pk)
            or user.is_negocio(obj.negocio.pk)
            or user.is_dueno_negocio(obj.negocio.pk)
            or (
                obj.negocio.franquicia
                and (
                    user.is_franquicia(obj.negocio.franquicia.pk)
                    or user.is_dueno_franquicia(obj.negocio.franquicia.pk)
                )
            )
        )

from rest_framework.permissions import BasePermission, SAFE_METHODS

class JerarquiaPermission(BasePermission):
    """
    Permiso jerárquico que valida el rol (Dueño, Admin, Empleado)
    en Franquicia > Negocio > Sede.
    """

    def has_permission(self, request, view):
        user = request.user
        # if user.is_superuser:
        #     return True

        # method = request.method
        name_url = view.basename

        if name_url in ("reservas", "negocio-reservas", "sede-reservas", "negocio-clientes"):
            return True

        return True

    def has_object_permission(self, request, view, obj):
        user = request.user
        if user.is_superuser:
            return True

        # Obtener el rol efectivo para el objeto
        role = None
        model_name = obj.__class__.__name__

        if model_name == "Franquicias":
            role = user.get_role_in_franquicia(obj.uuid)
        elif model_name == "Negocio":
            role = user.get_role_in_negocio(obj.nit)
        elif model_name == "Sede":
            role = user.get_role_in_sede(obj.uuid)
        elif model_name == "ColaboradresFranquicia":
            role = user.get_role_in_franquicia(obj.franquicia_id)
        elif model_name == "ColaboradoresNegocio":
            role = user.get_role_in_negocio(obj.negocio_id)
        elif model_name == "ColaboradoresSede":
            role = user.get_role_in_sede(obj.sede_id)
        elif model_name in ("Puesto", "Tarifa"):
            role = user.get_role_in_sede(obj.sede_id)

        if role is None:
            return False

        # REGLAS DE ACCESO:

        # 1. Lectura (GET) permitida para cualquier staff (Dueño, Admin, Empleado)
        method = request.method
        print(method, role)
        if method in SAFE_METHODS:
            return True

        # 2. Dueño (-1) puede hacer todo
        if role == "-1":
            return True

        # 3. Administrador (0)

        if role == "0":
            # Puede gestionar colaboradores (pero no a sí mismo o a dueños, aunque eso se valida en lógica de negocio)
            if model_name in ("ColaboradresFranquicia", "ColaboradoresNegocio", "ColaboradoresSede"):
                return True
            # Si es Sede, Negocio o Franquicia no pueden crearla
            if method == 'POST':
                return False

            # En Sedes, puede gestionar Puestos y Tarifas
            if model_name in ("Puesto", "Tarifa"):
                return True

            # NO puede crear, editar o desactivar las entidades principales (Franquicia, Negocio, Sede)
            return False

        # 4. Empleado (1)
        # Si llegó aquí es una acción de escritura, lo cual no está permitido para empleados en estas entidades
        return False
