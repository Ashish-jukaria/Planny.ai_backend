# Generated by Django 3.2.4 on 2023-04-07 06:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0005_alter_order_state'),
        ('account', '0004_auto_20230403_1446'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tenant',
            name='owner_id',
        ),
        migrations.AddField(
            model_name='subscriptiondetail',
            name='payment',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='shop.payment'),
        ),
    ]
