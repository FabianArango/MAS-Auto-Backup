# Generated by Django 3.1.7 on 2021-06-28 13:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('db', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='backuphandler',
            name='what',
            field=models.CharField(max_length=50),
        ),
        migrations.AlterField(
            model_name='backuphandler',
            name='where',
            field=models.CharField(max_length=50),
        ),
        migrations.DeleteModel(
            name='BackupObject',
        ),
    ]
