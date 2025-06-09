import uuid, pprint, logging
from datetime import datetime

from .utils import download_favicon, get_image_path_for_session
from .models import Category, Link

logger = logging.getLogger(__name__)


# В сессии ключи:
SESSION_KEY_CATEGORIES = 'session_categories'
SESSION_KEY_LINKS = 'session_links'

# Формат:
# session_categories = [
#   {'id': временный_уникальный_идентификатор, 'name': 'Категория', 'image': None или путь, ...},
#   ...
# ]
#
# session_links = [
#   {'id': временный_уникальный_идентификатор, 'link': 'http://...', 'name': '...', 'categories': [category_id,...], 'description': '...'},
#   ...
# ]

""" Небольшие функции для работы с сессиями """
def get_last_session_links(request):
    return request.session.get(SESSION_KEY_LINKS, [])[:5]

def get_last_session_categories(request):
    return request.session.get(SESSION_KEY_CATEGORIES, [])[:5]

def get_links_by_session(request):
    return request.session.get(SESSION_KEY_LINKS, [])

def get_categories_by_session(request):
    return request.session.get(SESSION_KEY_CATEGORIES, [])

def get_session_link_by_id(request, link_id):
    return next((link for link in request.session.get(SESSION_KEY_LINKS, []) if link['id'] == link_id), None)

def get_session_category_by_id(request, category_id):
    return next((category for category in request.session.get(SESSION_KEY_CATEGORIES, []) if category['id'] == category_id), None)

def get_session_links_by_category(request, category_id):
    return [link for link in request.session.get(SESSION_KEY_LINKS, []) if 'categories' in link and category_id in link['categories']]

def get_true_path_for_session_media(category_links):
    for link in category_links:
        if link.get('favicon_image') and not link['favicon_image'].startswith('/media/'):
            link['favicon_image'] = f'/media/{link["favicon_image"]}'
    return None


""" Функции для работы с сессионными закладками """
def add_link_to_session(request, form):
    """ Создание новой ссылки в сессии """
    session_links = request.session.get(SESSION_KEY_LINKS, [])
    link_url = form.cleaned_data['link']

    if any(link['link'] == link_url for link in session_links):
        return False, "Эта ссылка уже добавлена в ваш список."
    else:
        # Генерируем уникальный идентификатор
        temp_id = str(uuid.uuid4())
        favicon_path = download_favicon(link_url)
        if not favicon_path:
            favicon_path = 'defaults/favicon_default.png'

        new_link_data = {
                        'id': temp_id,
                        'name': form.cleaned_data['name'],
                        'link': form.cleaned_data['link'],
                        'description': form.cleaned_data.get('description', ''),
                        'categories': [],
                        'favicon_image': favicon_path,
                        'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        }
        session_links.append(new_link_data)
        request.session[SESSION_KEY_LINKS] = session_links
        request.session.set_expiry(0)
        return True, 'Ссылка успешно добавлена в ваш список.'
    

def delete_session_link(request, link_id):
    """ Удаление ссылки из сессии """
    session_links = request.session.get(SESSION_KEY_LINKS, [])
    for i, link in enumerate(session_links):
        if link['id'] == link_id:
            del session_links[i]
            break
    request.session.modified = True
    return True


def edit_session_link(request, link, form):
    """ Редактирование ссылки в сессии """
    link['name'] = form.cleaned_data['name']
    link['link'] = form.cleaned_data['link']
    link['description'] = form.cleaned_data['description']
    request.session.modified = True
    return True


""" Функции для работы с сессионными категориями """
def add_category_to_session(request, new_category_name, session_categories):
    """ Создание новой категории в сессии """
    # Генерируем уникальный идентификатор
    temp_id = str(uuid.uuid4())
    session_id = request.session.session_key
    
    image = get_image_path_for_session(request=request) or 'defaults/category.png'
    
    new_category_data = {
        'id': temp_id,
        'name': new_category_name,
        'image': image,
        'session_id': session_id,
        'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    }
    session_categories.append(new_category_data)
    request.session[SESSION_KEY_CATEGORIES] = session_categories
    request.session.set_expiry(0)
    return True


def edit_session_category(request, category, form):
    """ Редактирование категории в сессии """
    category['name'] = form.cleaned_data['name']
    category['image'] = get_image_path_for_session(request=request)
    request.session.modified = True
    return True


def add_session_link_to_category(request, form, category_id):
    """ Добавление ссылки в категорию в сессии """
    selected_links = form.cleaned_data['categories']
    session_links = request.session.get(SESSION_KEY_LINKS, [])
    for link in session_links:
        if link['id'] in selected_links:
            if 'categories' not in link:
                link['categories'] = []
            if category_id not in link['categories']:
                link['categories'].append(category_id)
    request.session[SESSION_KEY_LINKS] = session_links
    return True


def remove_session_link_from_category(request, links, category_id, link_id):
    """ Удаление ссылки из категории в сессии """
    for i, link in enumerate(links):
        if link['id'] == link_id:
            links[i]['categories'].remove(category_id)
            break
    request.session.modified = True
    return True


def delete_session_category(request, category_id, categories):
    """ Удаление категории из сессии """
    for i, category in enumerate(categories):
        if category['id'] == category_id:
            del categories[i]
            break
    request.session.modified = True
    return True


def migrate_session_data_to_user(request, user):
    session_links = request.session.get(SESSION_KEY_LINKS, [])
    session_categories = request.session.get(SESSION_KEY_CATEGORIES, [])

    category_map = {}

    # Перенос сессионных категорий в базу данных
    for session_cat in session_categories:
        category = Category.objects.create(
            user_id=user,
            name=session_cat['name'],
            image=session_cat.get('image', None),
        )
        category_map[str(session_cat['id'])] = category


    # Перенос сессионных ссылок в базу данных
    for session_link in session_links:
        link = Link.objects.create(
            user_id=user,
            name=session_link['name'],
            link=session_link['link'],
            description=session_link.get('description', None),
            favicon_image=session_link.get('favicon_image', 'defaults/favicon_default.png'),
        )
    

        # Привязка категорий к закладкам
        for cat_id in session_link.get('categories', []):
            category = category_map.get(str(cat_id))
            if category:
                link.categories.add(category)

        link.save()
    request.session.pop(SESSION_KEY_LINKS)
    request.session.pop(SESSION_KEY_CATEGORIES) 
    logger.info("✅ Перенос завершён для пользователя: %s", user)

    return None