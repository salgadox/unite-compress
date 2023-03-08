# Generated by Django 4.0.8 on 2023-03-03 15:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0001_initial'),
        ('files', '0004_convertingcommand_compression_rate'),
    ]

    operations = [
        migrations.AddField(
            model_name='file',
            name='course',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='files', to='courses.course'),
        ),
    ]