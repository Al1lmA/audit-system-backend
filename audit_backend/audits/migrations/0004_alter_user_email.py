# Generated by Django 5.2.1 on 2025-05-15 11:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('audits', '0003_remove_company_last_audit'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='email',
            field=models.EmailField(max_length=254, unique=True),
        ),
    ]
