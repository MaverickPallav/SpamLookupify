# Generated by Django 5.1.2 on 2024-11-01 15:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('SpamLookupify', '0007_remove_spamreport_contact'),
    ]

    operations = [
        migrations.AddField(
            model_name='contact',
            name='is_anonymous',
            field=models.BooleanField(default=False),
        ),
    ]
