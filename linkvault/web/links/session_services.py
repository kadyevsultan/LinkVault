import uuid
from datetime import datetime

from .utils import download_favicon

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

def get_last_session_links(request):
    return request.session.get(SESSION_KEY_LINKS, [])[:5]

def get_last_session_categories(request):
    return request.session.get(SESSION_KEY_CATEGORIES, [])[:5]

def get_links_by_session(request):
    return request.session.get(SESSION_KEY_LINKS, [])

def get_session_link_by_id(request, link_id):
    return next((link for link in request.session.get(SESSION_KEY_LINKS, []) if link['id'] == link_id), None)


def add_link_to_session(request, form):
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
    session_links = request.session.get(SESSION_KEY_LINKS, [])
    for i, link in enumerate(session_links):
        if link['id'] == link_id:
            del session_links[i]
            break
    request.session.modified = True
    return True