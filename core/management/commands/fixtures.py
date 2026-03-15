from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.apps import apps
from django.db import models
import os, json

MANUALES = (
    "tipo_id_usuarios", "status", "tipo_colaborador"
)


class Command(BaseCommand):
    help = "Ejecutar fixtures (datos defualt) de la app"

    def add_arguments(self, parser):
        parser.add_argument(
            "fixture", nargs="?", type=str, help="nombre del fixture a ejecutar"
        )
        parser.add_argument(
            "--all", action="store_true", help="ejecutar todos los fixtures"
        )

    def handle(self, *args, **options):
        if archivo := options.get("fixture", None):
            fxt_path = self.fixtures(archivo)
            if not fxt_path:
                self.stderr.write(f"Fixture {archivo} no encontrada")
                return

            file_name = os.path.basename(fxt_path)
            # if "usuarios" in file_name:
            #     self._fixture_usuario(fxt_path)
            #     return
            # self.fixture_is_manual(file_name):
            self._fixtures_manuales(fxt_path)
            return

            self._cargar_fixture(file_name)

        elif options.get("all", None):
            fixtures = self.fixtures()
            assert isinstance(fixtures, list), f'"fixtures" no es una lista'
            for fxt_path in fixtures:
                file_name = os.path.basename(fxt_path)
                # if "usuarios" in file_name:
                #     self._fixture_usuario(fxt_path)
                #     continue
                if self.fixture_is_manual(file_name):
                    self._fixtures_manuales(fxt_path)
                    continue
                self._cargar_fixture(file_name)

        else:
            self.stderr.write("Debe especificar un fixture o el flag --all")

    def fixtures(self, fixture_name: str = None):
        fixtures = []
        for app_conf in sorted(apps.get_app_configs(), key=lambda x: x.name):
            app_name = app_conf.name
            app_path = app_conf.path

            self.stdout.write(f"Examinando app {app_name}")

            fixtures_dir = os.path.join(app_path, "fixtures")
            if not os.path.exists(fixtures_dir):
                self.stderr.write(f"-> App sin fixtures")
                continue
            elif not os.path.isdir(fixtures_dir):
                self.stderr.write(f"-> Los fixtures es un archivo, no una caperta")
                continue

            if fixture_name:
                self.stdout.write(f"-> Buscando fixture {fixture_name}")

                file = next(
                    (file for file in os.listdir(fixtures_dir) if fixture_name in file),
                    None,
                )

                return os.path.join(fixtures_dir, file) if file else None

            for file in sorted(os.listdir(fixtures_dir)):
                if not file.endswith(".json"):
                    continue
                fixtures.append(os.path.join(fixtures_dir, file))

        return fixtures

    def _cargar_fixture(self, file: str):
        self.stdout.write(f"Cargando fixture {file}")
        try:
            call_command("loaddata", file)
        except Exception as e:
            self.stderr.write(f"Error al cargar fixture {file} desde comando: {e}")

    def _fixture_usuario(self, path_file: str):
        self.stdout.write(f"Insertando usuarios")
        with open(path_file, "r", encoding="utf-8") as file:
            datos_file = json.load(file)

        model_usuario = apps.get_model("core", "Usuarios")
        for data in datos_file:
            user_data = data.get("fields")

            try:
                model_usuario.objects.get(pk=user_data.get("numero_id"))
            except model_usuario.DoesNotExist:
                model_usuario.objects.create_user(**user_data)

    def _fixtures_manuales(self, path_file):
        with open(path_file, "r", encoding="utf-8") as file:
            datos_file = json.load(file)

        app_name, model_name = datos_file[0].get("model").split(".")
        model_class = apps.get_model(app_name, model_name)

        self.stdout.write(f"Insertando en {model_name}")
        model_class.objects.bulk_create(
            [model_class(**self._revisar_empresas(data, model_class)) for data in datos_file],
            ignore_conflicts=True,
        )

    def _revisar_empresas(self, data, model_class):
        def params(model_class, empresa=None):
            return {
                key_data: empresa if empresa and key_data == "empresa" else self._revisar_fks(model_class, key_data, value_data)
                for key_data, value_data in data.get("fields").items()
            }

        # valor_empresa = data.get("fields").get("empresa") or None
        # if valor_empresa == "*":
        #     from core.models import Empresas

        #     for empresa in Empresas.objects.all():
        #         return params(model_class, empresa)

        return params(model_class)

    def _revisar_fks(self, model_class, key, value):
        field = next(
            (
                field
                for field in model_class._meta.get_fields()
                if field.name == key
                and isinstance(field, (models.ForeignKey, models.OneToOneField))
            ),
            None,
        )
        if not field:
            return value

        model_related = field.related_model
        return model_related.objects.get(pk=value)

    def fixture_is_manual(self, file_name):
        return any([manual in file_name for manual in MANUALES])