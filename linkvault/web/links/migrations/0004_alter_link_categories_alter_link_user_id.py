# Generated by Django 4.2.20 on 2025-04-11 09:14

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('links', '0003_alter_link_favicon_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='link',
            name='categories',
            field=models.ManyToManyField(blank=True, related_name='category_links', to='links.category'),
        ),
        migrations.AlterField(
            model_name='link',
            name='user_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_links', to=settings.AUTH_USER_MODEL),
        ),
    ]
