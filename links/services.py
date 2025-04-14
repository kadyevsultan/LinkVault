from datetime import datetime

from .models import Link, Category

actual_year = datetime.now().year


# Все ссылки определенного пользователя
def get_links_by_user(request):
    if request.user.is_authenticated:
        return Link.objects.filter(user_id=request.user)
    else:
        return None
    

# Последние добавленные закладки, с ограничением в 5
def get_last_links(user):
    if user.is_authenticated:
        return Link.objects.filter(user_id=user).order_by('-created_at')[:5]
    else:
        return None
    
    
# Последние добавленные категории, с ограничением в 5
def get_last_categories(user):
    if user.is_authenticated:
        return Category.objects.filter(user_id=user).order_by('-created_at')[:5]
    else:
        return None


# Все категории определенного пользователя
def get_categories_by_user(request):
    if request.user.is_authenticated:
        return Category.objects.filter(user_id=request.user)
    else:
        return None
    

# Все закладки определенной категории
def get_links_by_category(category):
    links = Link.objects.filter(categories=category)
    return links


# Создание категории от формы
def create_or_edit_category_from_form(form, user, image):
    category = form.save(commit=False)
    category.user_id = user
    category.image = image
    category.save()
    return category


# Сервис для формы AddLinksToCategoryForm 
def get_links_by_user_for_category(user, category):
    return Link.objects.filter(user_id=user).exclude(categories=category)