# Generated by Django 4.2.5 on 2024-02-06 19:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0002_alter_item_list_model'),
    ]

    operations = [
        migrations.AddField(
            model_name='item_list',
            name='desc',
            field=models.TextField(default='def_description'),
        ),
    ]
