# Generated by Django 5.1.2 on 2024-11-01 05:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('SpamLookupify', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='name',
            field=models.CharField(blank=True, max_length=100),
        ),
    ]
