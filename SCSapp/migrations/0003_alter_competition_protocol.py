# Generated by Django 4.0.3 on 2022-09-13 09:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('SCSapp', '0002_alter_competition_organizername_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='competition',
            name='protocol',
            field=models.FileField(blank=True, null=True, upload_to='protocols', verbose_name='Протокол'),
        ),
    ]
