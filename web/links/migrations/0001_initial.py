# Generated by Django 4.2.20 on 2025-04-02 12:05

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('image', models.ImageField(blank=True, null=True, upload_to='category_images/')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='categories', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Link',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('link', models.TextField()),
                ('name', models.CharField(max_length=50)),
                ('description', models.TextField(blank=True, max_length=254, null=True)),
                ('favicon_image', models.ImageField(blank=True, default='defaults/favicon_default.png', null=True, upload_to='link_favicons/')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('categories', models.ManyToManyField(blank=True, null=True, related_name='link_set', to='links.category')),
                ('user_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='links', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'indexes': [models.Index(fields=['user_id', 'created_at'], name='links_link_user_id_ff5a41_idx')],
                'unique_together': {('user_id', 'link')},
            },
        ),
        migrations.AddIndex(
            model_name='category',
            index=models.Index(fields=['user_id', 'created_at'], name='links_categ_user_id_145a30_idx'),
        ),
        migrations.AlterUniqueTogether(
            name='category',
            unique_together={('user_id', 'name')},
        ),
    ]
