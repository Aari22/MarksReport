# Generated by Django 4.2.3 on 2023-07-15 13:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0009_alter_customuser_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='id',
            field=models.IntegerField(default=716, primary_key=True, serialize=False),
        ),
    ]
