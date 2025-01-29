# Generated by Django 5.0.2 on 2024-10-15 07:40

import activities.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('activities', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='fileupdatehistory',
            name='user_id',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='fileupdatehistory',
            name='contents',
            field=models.FileField(upload_to=activities.models.set_upload_to),
        ),
    ]
