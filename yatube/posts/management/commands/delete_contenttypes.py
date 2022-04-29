from django.core.management.base import BaseCommand


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        from django.contrib.contenttypes.models import ContentType
        ContentType.objects.all().delete()
