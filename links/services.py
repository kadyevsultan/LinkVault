from datetime import datetime

from .models import Link, Category

actual_year = datetime.now().year


def get_links_by_user(request):
    if request.user.is_authenticated:
        return Link.objects.filter(user_id=request.user)
    else:
        return None
    

def get_last_links(user):
    if user.is_authenticated:
        return Link.objects.filter(user_id=user).order_by('-created_at')[:5]
    else:
        return None


def get_categories_by_user(request):
    if request.user.is_authenticated:
        return Category.objects.filter(user_id=request.user)
    else:
        return None