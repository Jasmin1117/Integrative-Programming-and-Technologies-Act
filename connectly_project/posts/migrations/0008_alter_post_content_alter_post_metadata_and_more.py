# Generated by Django 5.1.5 on 2025-02-12 12:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0007_post_metadata_post_post_type_post_title'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='content',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='post',
            name='metadata',
            field=models.JSONField(default=dict),
        ),
        migrations.AlterField(
            model_name='post',
            name='post_type',
            field=models.CharField(choices=[('text', 'Text'), ('image', 'Image'), ('video', 'Video')], max_length=10),
        ),
        migrations.AlterField(
            model_name='post',
            name='title',
            field=models.CharField(max_length=255),
        ),
    ]
