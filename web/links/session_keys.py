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