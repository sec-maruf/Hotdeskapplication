# Generated by Django 5.0 on 2024-02-05 23:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hotdesk', '0007_alter_desk_availability'),
    ]

    operations = [
        migrations.AlterField(
            model_name='desk',
            name='availability',
            field=models.BooleanField(default=True),
        ),
    ]
