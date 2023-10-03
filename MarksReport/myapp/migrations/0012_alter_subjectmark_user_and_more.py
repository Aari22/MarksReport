# Generated by Django 4.2.3 on 2023-07-15 15:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0011_rename_user_id_subjectmark_user_alter_customuser_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subjectmark',
            name='user',
            field=models.ForeignKey(db_column='user_id', on_delete=django.db.models.deletion.CASCADE, to='myapp.customuser'),
        ),
        migrations.RenameField(
            model_name='subjectmark',
            old_name='user',
            new_name='user_id',
        ),
        migrations.AlterField(
            model_name='customuser',
            name='id',
            field=models.IntegerField(default=822, primary_key=True, serialize=False),
        ),
    ]
