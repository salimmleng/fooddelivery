# Generated by Django 5.0.6 on 2024-10-03 17:35

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('food', '0003_review'),
    ]

    operations = [
        migrations.AlterField(
            model_name='review',
            name='order',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='food.order'),
        ),
    ]