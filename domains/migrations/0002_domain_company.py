# Generated by Django 4.1.2 on 2022-11-22 02:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('companies', '0006_company_created_by'),
        ('domains', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='domain',
            name='company',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='companies.company'),
        ),
    ]
