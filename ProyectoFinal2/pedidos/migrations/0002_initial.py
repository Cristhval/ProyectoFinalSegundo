# Generated by Django 5.1.5 on 2025-01-30 03:32

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('menus', '0002_initial'),
        ('pedidos', '0001_initial'),
        ('util', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='itempedido',
            name='cliente',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='item_pedido_list', to='util.cliente'),
        ),
        migrations.AddField(
            model_name='itempedido',
            name='producto',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='menus.producto'),
        ),
        migrations.AddField(
            model_name='pedido',
            name='cliente',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pedidos_cliente', to='util.cliente'),
        ),
        migrations.AddField(
            model_name='pedido',
            name='item_pedido_list',
            field=models.ManyToManyField(blank=True, to='pedidos.itempedido'),
        ),
        migrations.AddField(
            model_name='historial',
            name='pedidos',
            field=models.ManyToManyField(to='pedidos.pedido'),
        ),
        migrations.AddField(
            model_name='registrohistorico',
            name='pedidos',
            field=models.ManyToManyField(blank=True, editable=False, to='pedidos.pedido'),
        ),
        migrations.AddField(
            model_name='restaurante',
            name='clientes',
            field=models.ManyToManyField(blank=True, to='util.cliente'),
        ),
        migrations.AddField(
            model_name='restaurante',
            name='meseros',
            field=models.ManyToManyField(blank=True, to='util.mesero'),
        ),
        migrations.AddField(
            model_name='restaurante',
            name='pedidos',
            field=models.ManyToManyField(blank=True, to='pedidos.pedido'),
        ),
        migrations.AddField(
            model_name='restaurante',
            name='personal_cocina_list',
            field=models.ManyToManyField(blank=True, to='util.personalcocina'),
        ),
    ]
