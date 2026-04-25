from django.shortcuts import get_object_or_404
from django.utils.functional import cached_property
from core.models.core import ModelCore
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.contrib.auth.hashers import make_password
from .utils import TipoIdentificacion, TipoVehiculo
import pgtrigger
from django.apps import apps

class UserManager(BaseUserManager):
    def create_user(self, tipo_id, tipo_usuario=None, password=None, *args, **kwargs):
        kwargs.update(
            {
                "tipo_id": (
                    TipoIdentificacion.objects.get(pk=tipo_id if tipo_id else "CC")
                    if not isinstance(tipo_id, TipoIdentificacion)
                    else tipo_id
                ),
                "password": make_password(
                    kwargs.get("numero_id") if password is None else password
                ),
            }
        )
        return self.return_user(*args, **kwargs)

    def create_superuser(self, *args, **kwargs):

        kwargs.update(
            {
                "is_staff": True,
                "is_superuser": True,
                "tipo_id": TipoIdentificacion.objects.get(pk=kwargs.get("tipo_id")),
                "password": make_password(
                    kwargs.get("password", kwargs.get("numero_id"))
                ),
            }
        )
        return self.return_user(*args, **kwargs)

    def return_user(self, *args, **kwargs):
        user = self.model(**kwargs)
        user.save()
        return user


class Usuarios(AbstractUser, ModelCore):
    first_name = None
    last_name = None
    username = None
    user_permissions = None
    groups = None
    estado = None

    REQUIRED_FIELDS = ("nombre",)
    USERNAME_FIELD = "numero_id"
    objects = UserManager()

    numero_id = models.CharField(
        max_length=10,
        primary_key=True,
        db_comment="Numero identifacion de la persona",
    )
    tipo_id = models.ForeignKey(
        TipoIdentificacion,
        default="CC",
        related_name="usuarios",
        on_delete=models.PROTECT,
        db_comment="Tipo de identificación",
    )
    nombre = models.TextField(db_comment="Nombre de la persona")
    password = models.TextField(db_comment="Contraseña del usuario")

    def is_franquicia(self, uuid):
        return self.franquicias.filter(franquicia=uuid).activos().exists()

    def get_role_in_franquicia(self, uuid):
        if self.is_superuser or self.dueno_franquicias.filter(uuid=uuid).activos().exists():
            return '-1'

        if colab := self.franquicias.filter(franquicia=uuid).activos().first():
            return colab.tipo_colaborador.pk

        return None

    def get_role_in_negocio(self, nit):
        if self.is_superuser or self.dueno_negocios.filter(nit=nit).activos().exists():
            return '-1'

        if colab := self.negocios.filter(negocio=nit).activos().first():
            return colab.tipo_colaborador.pk

        # Check parent franchise
        from negocios.models import Negocio
        try:
            negocio = Negocio.objects.get(pk=nit)
        except Negocio.DoesNotExist:
            return None

        if fr := getattr(negocio, 'franquicia'):
            return self.get_role_in_franquicia(fr.pk)

        return None

    def get_role_in_sede(self, uuid):
        if self.is_superuser or self.dueno_sedes.filter(uuid=uuid).activos().exists():
            return '-1'

        if colab := self.sedes.filter(sede=uuid).activos().first():
            return colab.tipo_colaborador.pk

        from negocios.models import Sede
        try:
            sede = Sede.objects.get(pk=uuid)
        except Sede.DoesNotExist:
            return None

        return self.get_role_in_negocio(sede.negocio.pk)

    @cached_property
    def is_dashboard_user(self):
        return (
            self.is_superuser
            or self.sedes.activos().exists()
            or self.negocios.activos().exists()
            or self.franquicias.activos().exists()
            or self.dueno_sedes.activos().exists()
            or self.dueno_negocios.activos().exists()
            or self.dueno_franquicias.activos().exists()
        )

    def reset_password(self):
        self.password = make_password(self.numero_id)
        self.save()

    class Meta:
        db_table = "usuarios"
        constraints = [
            models.UniqueConstraint(
                name="unico_tipo_numero",
                fields=("numero_id", "tipo_id"),
            ),
        ]
        triggers = [
            pgtrigger.Protect(
                name="prevenir_password_sin_hash",
                operation=pgtrigger.Insert | pgtrigger.Update,
                condition=~pgtrigger.Q(new__password__startswith="pbkdf2_"),
                when=pgtrigger.Before,
            ),
        ]


class VehiculosUsuario(ModelCore):
    pk = models.CompositePrimaryKey("usuario_id", "placa")
    usuario = models.ForeignKey(
        Usuarios, related_name="vehiculos", on_delete=models.DO_NOTHING
    )
    placa = models.CharField(
        max_length=10, unique=True, db_comment="Placa del vehiculo"
    )
    tipo_vehiculo = models.ForeignKey(TipoVehiculo, on_delete=models.PROTECT)

    class Meta:
        db_table = "vehiculos_usuario"
