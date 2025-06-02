from datetime import datetime

from django.shortcuts import get_object_or_404

from .models import Link, Category

actual_year = datetime.now().year


# Определенная закладка
def get_link_by_id(link_id):
    return get_object_or_404(Link, id=link_id)


# Определенная категория
def get_category_by_id_and_user(category_id, user_id):
    return get_object_or_404(Category, id=category_id, user_id=user_id)


# Сервис для удаления закладки
def delete_link(request, link_id):
    link = get_object_or_404(Link, id=link_id)
    if request.user != link.user_id:
        raise Exception('Вы не можете удалять закладки других пользователей')
    link.delete()
    return link

# Сервис для удаления категории
def delete_category(request, category_id): 
    category = get_object_or_404(Category, id=category_id)
    if request.user != category.user_id:
        raise Exception('Вы не можете удалять категории других пользователей')
    category.delete()
    return category


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

# Создание закладки от формы
def create_or_edit_link_from_form(form, user):
    link = form.save(commit=False)
    link.user_id = user
    link.save()
    return link



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



