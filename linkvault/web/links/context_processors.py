from .session_services import get_links_by_session

def show_exit_warning(request):
    if request.user.is_authenticated:
        return {'show_exit_warning': False}
    else:
        session_links = get_links_by_session(request)
        return {'show_exit_warning': bool(session_links)}