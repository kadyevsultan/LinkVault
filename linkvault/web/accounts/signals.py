from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from links.session_services import migrate_session_data_to_user, get_links_by_session, get_categories_by_session


@receiver(user_logged_in)
def migrate_session_data(sender, user, request, **kwargs):
    # Проверяем, есть ли данные в сессии
    session_links = get_links_by_session(request)
    session_categories = get_categories_by_session(request)

    if session_links or session_categories:
        migrate_session_data_to_user(request, user)