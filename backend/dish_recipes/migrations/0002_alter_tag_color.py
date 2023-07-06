# Generated by Django 4.2.2 on 2023-07-06 14:27

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dish_recipes', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tag',
            name='color',
            field=models.CharField(max_length=7, unique=True, validators=[django.core.validators.RegexValidator(message='Введенное значение не является цветом в формате HEX', regex='^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$')], verbose_name='Цветовой HEX-код'),
        ),
    ]
