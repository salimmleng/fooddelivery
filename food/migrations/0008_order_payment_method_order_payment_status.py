# Generated by Django 5.1.1 on 2024-10-30 16:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('food', '0007_remove_order_card_number_remove_order_cvv_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='payment_method',
            field=models.CharField(default='', max_length=20),
        ),
        migrations.AddField(
            model_name='order',
            name='payment_status',
            field=models.CharField(default='unpaid', max_length=20),
        ),
    ]