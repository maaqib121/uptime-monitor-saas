# Generated by Django 4.1.10 on 2023-04-26 23:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('countries', '0001_initial'),
        ('domains', '0006_alter_domain_options'),
    ]

    operations = [
        migrations.AlterField(
            model_name='domain',
            name='country',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='countries.country'),
        ),
    ]
