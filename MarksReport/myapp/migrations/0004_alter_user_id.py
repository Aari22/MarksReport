# Generated by Django 4.2.3 on 2023-07-13 02:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0003_alter_user_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='id',
            field=models.IntegerField(default=961, primary_key=True, serialize=False),
        ),
    ]
