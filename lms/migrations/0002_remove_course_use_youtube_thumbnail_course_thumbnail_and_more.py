# Generated by Django 5.2.3 on 2025-07-08 02:04

import cloudinary.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lms', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='course',
            name='use_youtube_thumbnail',
        ),
        migrations.AddField(
            model_name='course',
            name='thumbnail',
            field=cloudinary.models.CloudinaryField(blank=True, max_length=255, null=True, verbose_name='thumbnail'),
        ),
        migrations.AlterField(
            model_name='course',
            name='image',
            field=models.ImageField(default='https://via.placeholder.com/300', upload_to='courses/'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='course',
            name='video_file',
            field=cloudinary.models.CloudinaryField(blank=True, max_length=255, null=True, verbose_name='video'),
        ),
    ]
