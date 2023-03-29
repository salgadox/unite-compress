from django.conf import settings
from django.db import migrations


def alter_site_domain(apps, schema_editor, domain):
    Site = apps.get_model("sites", "Site")
    Site.objects.filter(pk=settings.SITE_ID).update(domain=domain)


def alter_site_forward(apps, schema_editor):
    alter_site_domain(apps, schema_editor, "e-learning4all.app")


def alter_site_backward(apps, schema_editor):
    alter_site_domain(apps, schema_editor, "unite.academy")


class Migration(migrations.Migration):
    dependencies = [
        ("sites", "0003_set_site_domain_and_name"),
    ]

    operations = [
        migrations.RunPython(alter_site_forward, alter_site_backward),
    ]
