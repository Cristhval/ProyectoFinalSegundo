# Generated by Django 5.1.5 on 2025-02-01 23:16

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('menus', '0001_initial'),
        ('util', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='producto',
            name='impuestos',
            field=models.ManyToManyField(blank=True, to='util.impuesto'),
        ),
    ]
