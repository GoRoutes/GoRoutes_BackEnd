import subprocess
import os
import shutil
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    help = 'Apaga o banco de dados, remove pastas de migrações e executa os comandos makemigrations e migrate para diferentes apps'

    def handle(self, *args, **kwargs):
        apps = ["authentication", "goroutes"]
        db_path = 'db.sqlite3'

        if os.path.exists(db_path):
            self.stdout.write('Apagando o banco de dados...')
            os.remove(db_path)

        # for app in apps:
        #     migrations_path = os.path.join(app, 'migrations')
        #     if os.path.exists(migrations_path):
        #         self.stdout.write(f'Removendo a pasta de migrações para {app}...')
        #         shutil.rmtree(migrations_path)

        for app in apps:
            self.stdout.write(f'Executando makemigrations para {app}...')
            subprocess.run(['pdm', 'makemigrations', app], check=True)
            
            self.stdout.write(f'Executando migrate para {app}...')
            subprocess.run(['pdm' ,  'migrate', app], check=True)
        
        subprocess.run(['pdm', 'migrate'], check=True)

        # Create superuser
        User = get_user_model()
        if not User.objects.filter(email='admin@admin.com').exists():
            self.stdout.write("Criando superusuário admin...")
            User.objects.create_superuser(email='admin@admin.com', password='admin')
            users = list(User.objects.all())

        self.stdout.write(self.style.SUCCESS('Comandos executados com sucesso para todos os apps!'))
