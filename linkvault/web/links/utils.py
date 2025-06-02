import os
import requests
import logging
from linkvault import settings

from urllib.parse import urlparse

logger = logging.getLogger(__name__)

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
        logger.warning(f'Произошла ошибка при скачивании favicon: {favicon_url}')
        return None # нет favicon
        


def download_image_if_not_exists(image_url: str, media_subdir: str = 'category_images') -> str:
    """
    Скачивает изображение по URL и сохраняет в папку media/category_images, 
    если оно ещё не существует. Возвращает относительный путь к файлу.
    """
    from django.core.files.base import ContentFile
    from django.core.files.storage import default_storage

    filename = os.path.basename(image_url)
    media_path = os.path.join(media_subdir, filename)
    full_path = os.path.join(settings.MEDIA_ROOT, media_path)

    if not os.path.exists(full_path):
        response = requests.get(image_url)
        if response.status_code == 200:
            default_storage.save(media_path, ContentFile(response.content))
    
    return media_path


def get_image_from_request(request):
    """
    Возвращает изображение из request: либо файл, либо путь к скачанному изображению из URL.
    """
    if 'image_file' in request.FILES:
        return request.FILES['image_file']
    
    image_url = request.POST['image_url']
    if image_url:
        return download_image_if_not_exists(image_url=image_url)

    return None


def get_image_path_for_session(request):
    """
    Сохраняет изображение (если оно загружено пользователем) и возвращает путь к файлу.
    """
    if 'image_file' in request.FILES:
        image = request.FILES['image_file']
        image_path = os.path.join('category_images', image.name)
        full_image_path = os.path.join(settings.MEDIA_ROOT, image_path)
        
        os.makedirs(os.path.dirname(full_image_path), exist_ok=True)

        # Сохраняем изображение на диск
        with open(full_image_path, 'wb') as f:
            for chunk in image.chunks():
                f.write(chunk)
            
        return image_path
    elif 'image_url' in request.POST:
        image_url = request.POST['image_url']
        if image_url:
            return download_image_if_not_exists(image_url=image_url)
    
    # Изображение по умолчанию
    return 'defaults/category.png'