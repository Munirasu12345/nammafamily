from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    help = 'Reset (or set) a superuser password from the command line. Usage: manage.py reset_admin_password --username=<username> --password=<password>'

    def add_arguments(self, parser):
        parser.add_argument('--username', type=str, required=True, help='Username of the account')
        parser.add_argument('--password', type=str, required=True, help='New password to set')

    def handle(self, *args, **options):
        User = get_user_model()
        username = options['username']
        password = options['password']

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise CommandError(f"User '{username}' does not exist")

        user.set_password(password)
        user.save()

        self.stdout.write(self.style.SUCCESS(f"Password for user '{username}' has been set."))
