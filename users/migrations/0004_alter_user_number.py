# Generated by Django 4.2.4 on 2023-08-19 08:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_user_number'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='number',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
    ]