# Generated by Django 5.1.5 on 2025-02-02 01:10

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pedidos', '0003_alter_registrohistorico_options_and_more'),
        ('util', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='pedido',
            name='mesero',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='util.mesero'),
        ),
    ]
