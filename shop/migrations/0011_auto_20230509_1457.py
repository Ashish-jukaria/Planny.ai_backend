# Generated by Django 3.2.4 on 2023-05-09 09:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0005_auto_20230407_1149'),
        ('shop', '0010_auto_20230502_1944'),
    ]

    operations = [
        migrations.AddField(
            model_name='productpricevariation',
            name='tenant',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='account.tenant'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='productvariation',
            name='tenant',
            field=models.ForeignKey(default=2, on_delete=django.db.models.deletion.CASCADE, to='account.tenant'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='variationcombos',
            name='tenant',
            field=models.ForeignKey(default=6, on_delete=django.db.models.deletion.CASCADE, to='account.tenant'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='category',
            name='products',
            field=models.ManyToManyField(blank=True, related_name='categories', to='shop.Product'),
        ),
        migrations.AlterField(
            model_name='order',
            name='state',
            field=models.JSONField(default={'state_list': [{'action': None, 'body': {'media_height': None, 'media_width': None, 'thumbnail_image': {'height': None, 'url': None, 'width': None}, 'value': 'Welcome to Aikam\nNow get your medicines at your doorstep with huge discount'}, 'created_on': 'May 2023, 14:57PM', 'sender': 'AIKAM', 'state_type': 'TEXT'}, {'action': 'REQUEST_CALLBACK', 'body': {'media_height': None, 'media_width': None, 'thumbnail_image': {'height': None, 'url': None, 'width': None}, 'value': None}, 'created_on': 'May 2023, 14:57PM', 'sender': 'AIKAM', 'state_type': 'REQUEST_CALLBACK'}, {'action': 'UPLOAD_PRESCRIPTION', 'body': {'media_height': None, 'media_width': None, 'thumbnail_image': {'height': None, 'url': None, 'width': None}, 'value': None}, 'created_on': 'May 2023, 14:57PM', 'sender': 'AIKAM', 'state_type': 'UPLOAD_PRESCRIPTION'}]}),
        ),
        migrations.CreateModel(
            name='Toppings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('updated_on', models.DateTimeField(auto_now=True)),
                ('is_active', models.BooleanField(default=False)),
                ('name', models.CharField(max_length=100)),
                ('image', models.ImageField(blank=True, null=True, upload_to='Toppins', verbose_name='Toppings Images')),
                ('price', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='shop.productpricevariation')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='shop.product')),
                ('tenant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='account.tenant')),
            ],
            options={
                'verbose_name_plural': 'Toppings',
            },
        ),
    ]