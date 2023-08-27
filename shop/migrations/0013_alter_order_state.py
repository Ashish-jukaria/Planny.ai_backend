# Generated by Django 3.2.4 on 2023-08-27 14:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0012_alter_order_state'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='state',
            field=models.JSONField(default={'state_list': [{'action': None, 'body': {'media_height': None, 'media_width': None, 'thumbnail_image': {'height': None, 'url': None, 'width': None}, 'value': 'Welcome to Aikam\nNow get your medicines at your doorstep with huge discount'}, 'created_on': 'August 2023, 20:25PM', 'sender': 'AIKAM', 'state_type': 'TEXT'}, {'action': 'REQUEST_CALLBACK', 'body': {'media_height': None, 'media_width': None, 'thumbnail_image': {'height': None, 'url': None, 'width': None}, 'value': None}, 'created_on': 'August 2023, 20:25PM', 'sender': 'AIKAM', 'state_type': 'REQUEST_CALLBACK'}, {'action': 'UPLOAD_PRESCRIPTION', 'body': {'media_height': None, 'media_width': None, 'thumbnail_image': {'height': None, 'url': None, 'width': None}, 'value': None}, 'created_on': 'August 2023, 20:25PM', 'sender': 'AIKAM', 'state_type': 'UPLOAD_PRESCRIPTION'}]}),
        ),
    ]
