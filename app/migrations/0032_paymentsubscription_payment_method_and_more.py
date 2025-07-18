# Generated by Django 5.2 on 2025-05-21 08:39

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0031_alter_adminanswer_message_lastsearch'),
    ]

    operations = [
        migrations.AddField(
            model_name='paymentsubscription',
            name='payment_method',
            field=models.CharField(choices=[('BALANCE', 'Balance'), ('PAYME', 'payme')], db_default='BALANCE', max_length=30),
        ),
        migrations.AlterField(
            model_name='moviecomment',
            name='movie',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='app.movie'),
        ),
    ]
