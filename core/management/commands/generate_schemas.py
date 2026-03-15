from django.core.management.base import BaseCommand
from django.db import connection
from django.conf import settings

new_schemas = {
    # 'administracion': '',
}

class Command(BaseCommand):
    help = 'Genera los esquemas de los modelos'

    def handle(self, *args, **kwargs):
        db_user = settings.DATABASES['default']['USER']
        with connection.cursor() as cursor:
            for schema, description in new_schemas.items():
                try:
                    cursor.execute(f"CREATE SCHEMA IF NOT EXISTS {schema}")
                    cursor.execute(f"COMMENT ON SCHEMA {schema} IS '{description}'")
                    
                    cursor.execute(f'''
                        GRANT USAGE ON SCHEMA "{schema}" TO "{db_user}";
                        GRANT CREATE ON SCHEMA "{schema}" TO "{db_user}";
                        GRANT ALL ON ALL TABLES IN SCHEMA "{schema}" TO "{db_user}";
                    ''')
                except Exception as e:
                    self.stdout.write(f'Error al crear el esquema {schema}: {e}')
            