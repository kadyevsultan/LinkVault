import os
import requests
from linkvault import settings

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage

from urllib.parse import urlparse


def download_favicon(link):
    """Скачивает favicon по ссылке и возвращает путь к сохранённому файлу"""
    parsed_url = urlparse(link)
    domain = parsed_url.netloc.lower().replace('www.', '')
    
    favicon_dir = os.path.join(settings.MEDIA_ROOT, 'favicons')
    if not os.path.exists(favicon_dir):
        os.makedirs(favicon_dir)
    
    filename = f"{domain.replace('.', '_')}.ico"
    
    filepath = os.path.join(favicon_dir, filename)
    
    if os.path.exists(filepath):
        return os.path.relpath(filepath, settings.MEDIA_ROOT)
    
    # URL для скачивания favicon с разных сайтов
    favicon_url = f'https://t3.gstatic.com/faviconV2?client=SOCIAL&type=FAVICON&fallback_opts=TYPE,SIZE,URL&url=http://{domain}&size=64'
    
    try:
        response = requests.get(favicon_url, stream=True)
        response.raise_for_status()
        
        if len(response.content) < 50:
            return None # нет favicon
        
        # Сохраняем файл в media
        with open(filepath, 'wb') as f:
            f.write(response.content)
        
        path = os.path.relpath(filepath, settings.MEDIA_ROOT)
        return path
    
    except requests.RequestException:    
        return None # нет favicon
        
