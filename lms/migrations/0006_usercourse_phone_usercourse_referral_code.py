# Generated by Django 5.2.3 on 2025-07-10 09:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lms', '0005_alter_course_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='usercourse',
            name='phone',
            field=models.CharField(blank=True, max_length=15, null=True),
        ),
        migrations.AddField(
            model_name='usercourse',
            name='referral_code',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
