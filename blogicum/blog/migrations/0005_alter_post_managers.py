# Generated by Django 3.2.16 on 2023-08-03 10:10

from django.db import migrations
import django.db.models.manager


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0004_auto_20230803_1221'),
    ]

    operations = [
        migrations.AlterModelManagers(
            name='post',
            managers=[
                ('published_posts', django.db.models.manager.Manager()),
            ],
        ),
    ]
