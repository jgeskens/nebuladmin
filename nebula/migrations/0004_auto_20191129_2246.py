# Generated by Django 2.2.7 on 2019-11-29 22:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nebula', '0003_auto_20191127_2122'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='member',
            name='deployment_template',
        ),
        migrations.AddField(
            model_name='member',
            name='deployment',
            field=models.CharField(blank=True, choices=[('amd64_ubuntu_runit', 'Ubuntu runit amd64')], max_length=100),
        ),
    ]
