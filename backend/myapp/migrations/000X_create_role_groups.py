from django.db import migrations
from django.contrib.auth.models import Group

def create_role_groups(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    roles = ['it', 'rector', 'maintenance', 'warden', 'panel']
    for role in roles:
        Group.objects.get_or_create(name=role)

class Migration(migrations.Migration):
    dependencies = [
        ('myapp', '0001_initial'),
        ('auth', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_role_groups),
    ]