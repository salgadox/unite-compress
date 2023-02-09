# Generated by Django 4.0.8 on 2023-02-09 14:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('files', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='convertingcommand',
            name='match_by',
        ),
        migrations.RemoveField(
            model_name='convertingcommand',
            name='match_regex',
        ),
        migrations.AddField(
            model_name='convertingcommand',
            name='mime_regex',
            field=models.CharField(default='video/*', max_length=50, verbose_name='Regex to match mime types'),
            preserve_default=False,
        ),
    ]
