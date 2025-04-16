from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import IntegrityError
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied

from .forms import LinkForm, EditLinkForm, CategoryForm, AddLinksToCategoryForm, EditCategoryForm

from .utils import get_image_from_request
from .services import actual_year
from .services import (
    get_links_by_user, get_last_links, get_categories_by_user, get_links_by_category, get_last_categories,
    create_or_edit_category_from_form,
    delete_link, get_link_by_id, create_or_edit_link_from_form, get_category_by_id_and_user, delete_category,
)


""" Главная страница """
def index_view(request):
    context = {
        'title': 'LinkVault - Главная',
        'actual_year': actual_year,
        'last_links': get_last_links(user=request.user),
        'last_categories': get_last_categories(user=request.user),
        'user': request.user
    }
    return render(request, 'links/index.html', context=context)


""" Закладки """
# Все закладки пользователя
def my_links_view(request):
    links = get_links_by_user(request)
    context = {
        'title': 'LinkVault - Мои Закладки',
        'links': links,
        'actual_year': actual_year,
    }
    return render(request, 'links/my-links.html', context=context)


""" Детальная информация о закладке """
def detail_link_view(request, link_id):
    link = get_link_by_id(link_id)
    context = {
        'title': f'LinkVault - {link.name}',
        'link': link,
        'actual_year': actual_year,
    }
    return render(request, 'links/detail-link.html', context=context)


""" Удаление закладки """
def delete_link_view(request, link_id):
    try:
        delete_link(link_id=link_id, request=request)
        messages.success(request, 'Закладка успешно удалена')
    except PermissionDenied: 
        messages.error(request, 'Вы не можете удалить эту закладку')
    except Exception as e:
        messages.error(request, f'Произошла ошибка при удалении закладки, попробуйте позже.')
    return redirect('links:my-links')


""" Добавление закладки """
def add_link_view(request):
    form = LinkForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        try:
            create_or_edit_link_from_form(form=form, user=request.user)
            messages.success(request, 'Ссылка успешно добавлена')
            return redirect('links:my-links')
        except IntegrityError:
            form.add_error("link", "Эта ссылка уже добавлена в ваш список.")
            messages.error(request, 'Эта ссылка уже добавлена в ваш список.')
    else:
        messages.error(request, 'Пожалуйста, исправьте ошибки в форме.')
        
    context = {
        'title': 'LinkVault - Добавить ссылку',
        'form': form,
        'actual_year': actual_year,
    }
    return render (request, 'links/add-link.html', context=context)


""" Редактирование закладки """
def edit_link_view(request, link_id):
    link = get_link_by_id(link_id)
    if request.method == 'POST':
        form = EditLinkForm(request.POST, instance=link)
        if form.is_valid():
            create_or_edit_link_from_form(form=form, user=request.user)
            messages.success(request, 'Ссылка успешно обновлена')
            return redirect('links:detail-link', link_id=link_id)
    else:
        form = EditLinkForm(instance=link)
        
    context = {
        'title': 'LinkVault - Редактирование ссылки',
        'form': form,
        'link': link,
        'actual_year': actual_year,
    }
    return render (request, 'links/edit-link.html', context=context)


""" Категории """
def my_categories_view(request):
    context = {
        'title': 'LinkVault - Мои Категории',
        'categories': get_categories_by_user(request),
        'actual_year': actual_year,
    }
    return render(request, 'categories/categories.html', context=context)


""" Добавление категории """
@login_required
def add_category_view(request):
    form = CategoryForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():   
        try:
            image = get_image_from_request(request=request)
            create_or_edit_category_from_form(form=form, user=request.user, image=image)
            
            messages.success(request, 'Категория успешно добавлена')
            return redirect('links:my-categories')
        except IntegrityError:
            form.add_error("name", "Эта категория уже добавлена в ваш список.")
        except Exception as e:
            messages.error(request, f'Произошла ошибка при добавлении категории: {str(e)}')
            return redirect('links:my-categories')

            
    context = {
        'title': 'LinkVault - Добавить категорию',
        'form': form,
        'actual_year': actual_year,
    }
    return render(request, 'categories/add-category.html', context=context)


""" Страница редактирования категории """
def edit_category_view(request, category_id):
    category = get_category_by_id_and_user(category_id=category_id, user_id=request.user)
    form = EditCategoryForm(request.POST or None, instance=category)
    if request.method == 'POST' and form.is_valid():
        try:
            image = get_image_from_request(request=request)
            create_or_edit_category_from_form(form=form, user=request.user, image=image)
            
            messages.success(request, 'Категория успешно обновлена')
            return redirect('links:my-categories')
        except Exception as e:
            messages.error(request, f'Произошла ошибка при обновлении категории.')
            return redirect('links:my-categories')
        
    context = {
        'title': 'LinkVault - Редактировать категорию',
        'form': form,
        'category': get_category_by_id_and_user(category_id=category_id, user_id=request.user),
        'actual_year': actual_year,
    }
    
    return render(request, 'categories/edit-category.html', context=context)


""" Сама категория и закладки внутри категории """
def links_by_category_view(request, category_id):
    category = get_category_by_id_and_user(category_id=category_id, user_id=request.user)
    context = {
        'title': f'LinkVault - {category.name}',
        'category': category,
        'links': get_links_by_category(category=category),
        'actual_year': actual_year,
    }
    return render(request, 'categories/links-by-category.html', context=context)


""" Добавить закладки в определенную категорию """
def add_links_to_category_view(request, category_id):
    category = get_category_by_id_and_user(category_id=category_id, user_id=request.user)
    form = AddLinksToCategoryForm(request.POST or None, user=request.user, category=category)
    
    if request.method == 'POST' and form.is_valid():
        try:
            links = form.cleaned_data['categories']
            for link in links:
                link.categories.add(category)
                link.save()
            messages.success(request, 'Закладки успешно добавлены в категорию')
        except Exception as e:
            messages.error(request, f'Произошла ошибка при добавлении закладок в категорию')
        return redirect('links:links-by-category', category_id=category_id)
        
    context = {
        'title': f'LinkVault - {category.name}',
        'category': category,
        'form': form,
        'actual_year': actual_year,
    }
    return render(request, 'categories/add-links-to-category.html', context=context)


""" Удаление самой категории """
def delete_category_view(request, category_id):
    if request.method == 'POST':
        try:
            delete_category(request=request, category_id=category_id)
            messages.success(request, 'Категория успешно удалена')
        except Exception as e:
            messages.error(request, f'Произошла ошибка при удалении категории')
    return redirect('links:my-categories')