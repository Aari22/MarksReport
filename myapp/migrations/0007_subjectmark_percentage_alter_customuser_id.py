# Generated by Django 4.2.3 on 2023-07-13 16:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0006_customuser_alter_subjectmark_user_id_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='subjectmark',
            name='percentage',
            field=models.FloatField(default=None),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='id',
            field=models.IntegerField(default=198, primary_key=True, serialize=False),
        ),
    ]