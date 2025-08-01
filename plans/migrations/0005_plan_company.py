# Generated by Django 4.1.2 on 2022-11-04 12:10

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('companies', '0005_company_is_subscription_active'),
        ('plans', '0004_plan_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='plan',
            name='company',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='companies.company'),
        ),
    ]
