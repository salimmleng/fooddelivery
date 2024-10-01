# Generated by Django 5.0.6 on 2024-09-30 19:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('food', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='order_status',
            field=models.CharField(choices=[('Delivered', 'Delivered'), ('Pending', 'Pending')], default='Pending', max_length=20),
        ),
    ]
