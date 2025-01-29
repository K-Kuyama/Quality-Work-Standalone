# Generated by Django 5.0.2 on 2024-10-06 09:08

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Activity',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_time', models.DateTimeField(unique=True)),
                ('duration', models.IntegerField()),
                ('distance_x', models.FloatField()),
                ('distance_y', models.FloatField()),
                ('strokes', models.IntegerField()),
                ('scrolls', models.IntegerField()),
                ('app', models.CharField(max_length=128)),
                ('title', models.CharField(max_length=256)),
            ],
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128)),
                ('color', models.CharField(max_length=128)),
            ],
        ),
        migrations.CreateModel(
            name='FileUpdateHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fileName', models.CharField(max_length=128)),
                ('uploadTime', models.DateTimeField()),
                ('contents', models.FileField(upload_to='uploads/')),
                ('startTime', models.DateTimeField()),
                ('endTime', models.DateTimeField()),
                ('dataCount', models.IntegerField()),
                ('status', models.CharField(max_length=128)),
            ],
        ),
        migrations.CreateModel(
            name='Perspective',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128)),
                ('color', models.CharField(max_length=128)),
                ('use_def_color', models.BooleanField()),
                ('categorize_model', models.CharField(max_length=128, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='CategorizedKeyWord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('word', models.CharField(max_length=128)),
                ('positive', models.BooleanField()),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='key_words', to='activities.category')),
            ],
        ),
        migrations.CreateModel(
            name='CategorizedActivity',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('app', models.CharField(max_length=128)),
                ('title', models.CharField(max_length=256)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='activities', to='activities.category')),
            ],
        ),
        migrations.AddField(
            model_name='category',
            name='perspective',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='categories', to='activities.perspective'),
        ),
    ]
