import os

from django.db import models
from django.contrib.auth import get_user_model

from urllib.parse import urlparse

from linkvault import settings
from .utils import download_favicon

User = get_user_model()

# Категории ссылок
class Category(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name='categories') # Связь с пользователем
    name = models.CharField(max_length=50) # Название категории
    image = models.ImageField(upload_to='category_images/', blank=True, null=True) # Изображение категории
    created_at = models.DateTimeField(auto_now_add=True) # Дата создания
    updated_at = models.DateTimeField(auto_now=True) # Дата обновления
    
    class Meta:
        unique_together = ('user_id', 'name') # Поле для уникального имени категории, предотвращение повторных названий категорий
        indexes = [
            models.Index(fields=['user_id', 'created_at']) # Индексы для полей по пользователю и даты создания, чтобы ускорить поиск для главной страницы
        ]
        
    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

# Ссылки
class Link(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_links') # Связь с пользователем
    link = models.TextField(blank=False, null=False) # Ссылка
    name = models.CharField(max_length=50) # Название ссылки
    description = models.TextField(blank=True, null=True, max_length=254) # Описание
    categories = models.ManyToManyField(Category, related_name='category_links', blank=True) # Связь с категориями
    favicon_image = models.ImageField(upload_to='favicons/', blank=True, null=True, default='defaults/favicon_default.png') # Изображение favicon
    created_at = models.DateTimeField(auto_now_add=True) # Дата создания
    updated_at = models.DateTimeField(auto_now=True) # Дата обновления
    
    class Meta:
        unique_together = ('user_id', 'link') # Поле для уникальной ссылки, предотвращение повторных ссылок
        indexes = [
            models.Index(fields=['user_id', 'created_at']) # Индексы для полей по пользователю и даты создания, чтобы ускорить поиск для главной страницы
        ]
        
    def save(self, *args, **kwargs):
        # Перед сохранением скачиваем файл по ссылке и сохраняем его как изображение favicon
        if not self.favicon_image or self.favicon_image.name == 'defaults/favicon_default.png':
            favicon_path = download_favicon(self.link)
            
            if favicon_path: # Если скачивание прошло успешно
                absolute_favicon_path = os.path.join(settings.MEDIA_ROOT, favicon_path)
                
                if os.path.exists(absolute_favicon_path) and self.favicon_image.name != favicon_path: # Если файл существует и его имя не совпадает с сохранённым
                    # Просто присваиваем путь, без пересохранения файла
                    self.favicon_image.name = favicon_path
            else:
                self.favicon_image = 'defaults/favicon_default.png'

        super().save(*args, **kwargs)
        
        
    def __str__(self):
        parsed_url = urlparse(self.link) # Парсинг ссылки
        domain = parsed_url.netloc # Домен
        
        if parsed_url.path or parsed_url.query or parsed_url.fragment: # Если есть путь, параметры или фрагмент ссылки
            return f'{self.name} - ({domain}{parsed_url.path[:20]}...)' # Возвращаем название ссылки, домен и первые 20 символов пути
        else:
            return f'{self.name} - ({domain})' # Возвращаем название ссылки и домен