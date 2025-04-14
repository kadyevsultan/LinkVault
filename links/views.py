from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import IntegrityError
from django.contrib.auth.decorators import login_required

from .forms import LinkForm, EditLinkForm, CategoryForm, AddLinksToCategoryForm, EditCategoryForm
from .models import Link, Category

from .utils import get_image_from_request
from .services import actual_year
from .services import (
    get_links_by_user, get_last_links, get_categories_by_user, get_links_by_category, get_last_categories,
    create_or_edit_category_from_form,
)


# Главная страница
def index_view(request):
    context = {
        'title': 'LinkVault - Главная',
        'actual_year': actual_year,
        'last_links': get_last_links(user=request.user),
        'last_categories': get_last_categories(user=request.user),
    }
    return render(request, 'links/index.html', context=context)


# Все закладки пользователя
def my_links_view(request):
    links = get_links_by_user(request)
    context = {
        'title': 'LinkVault - Мои Закладки',
        'links': links,
        'actual_year': actual_year,
    }
    return render(request, 'links/my-links.html', context=context)


# Детальная информация о закладке
def detail_link_view(request, link_id):
    link = get_object_or_404(Link, id=link_id)
    context = {
        'title': f'LinkVault - {link.name}',
        'link': link,
        'actual_year': actual_year,
    }
    return render(request, 'links/detail-link.html', context=context)


# Удаление закладки
def delete_link_view(request, link_id):
    link = get_object_or_404(Link, id=link_id)
    try:
        link.delete()
        messages.success(request, 'Закладка успешно удалена')
    except:
        messages.error(request, 'Произошла ошибка при удалении закладки, попробуйте позже.')
    return redirect('links:my-links')


# Добавление закладки
def add_link_view(request):
    if request.method == 'POST':
        form = LinkForm(request.POST)
        if form.is_valid():
            link = form.save(commit=False)
            link.user_id = request.user
            try:
                link.save()
                messages.success(request, 'Ссылка успешно добавлена')
                return redirect('links:my-links')
            except IntegrityError:
                form.add_error("link", "Эта ссылка уже добавлена в ваш список.")
                messages.error(request, 'Эта ссылка уже добавлена в ваш список.')
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме.')
    else:
        form = LinkForm()
        
    context = {
        'title': 'LinkVault - Добавить ссылку',
        'form': form,
        'actual_year': actual_year,
    }
    return render (request, 'links/add-link.html', context=context)


# Редактирование закладки
def edit_link_view(request, link_id):
    link = get_object_or_404(Link, id=link_id)
    if request.method == 'POST':
        form = EditLinkForm(request.POST, instance=link)
        if form.is_valid():
            form.save()
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


# КАТЕГОРИИ
def my_categories_view(request):
    context = {
        'title': 'LinkVault - Мои Категории',
        'categories': get_categories_by_user(request),
        'actual_year': actual_year,
    }
    return render(request, 'categories/categories.html', context=context)


# Добавление категории
@login_required
def add_category_view(request):
    if request.method == 'POST':   
        form = CategoryForm(request.POST)
        if form.is_valid():
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
    else:
        form = CategoryForm()
            
    context = {
        'title': 'LinkVault - Добавить категорию',
        'form': form,
        'actual_year': actual_year,
    }
    return render(request, 'categories/add-category.html', context=context)


# Страница редактирования категории
def edit_category_view(request, category_id):
    if request.method == 'POST':
        form = EditCategoryForm(request.POST, instance=get_object_or_404(Category, id=category_id, user_id=request.user))
        if form.is_valid():
            try:
                image = get_image_from_request(request=request)
                create_or_edit_category_from_form(form=form, user=request.user, image=image)
                
                messages.success(request, 'Категория успешно обновлена')
                return redirect('links:my-categories')
            except Exception as e:
                messages.error(request, f'Произошла ошибка при обновлении категории: {str(e)}')
                return redirect('links:my-categories')
    else:
        form = EditCategoryForm(instance=get_object_or_404(Category, id=category_id, user_id=request.user))
        
    context = {
        'title': 'LinkVault - Редактировать категорию',
        'form': form,
        'category': get_object_or_404(Category, id=category_id, user_id=request.user),
        'actual_year': actual_year,
    }
    
    return render(request, 'categories/edit-category.html', context=context)


# Сама категория и закладки внутри категории
def links_by_category_view(request, category_id):
    category = get_object_or_404(Category, id=category_id, user_id=request.user)
    context = {
        'title': f'LinkVault - {category.name}',
        'category': category,
        'links': get_links_by_category(category=category),
        'actual_year': actual_year,
    }
    return render(request, 'categories/links-by-category.html', context=context)


# Добавить закладки в определенную категорию
def add_links_to_category_view(request, category_id):
    category = get_object_or_404(Category, id=category_id, user_id=request.user)
    
    if request.method == 'POST':
        form = AddLinksToCategoryForm(request.POST, user=request.user, category=category)
        try:
            if form.is_valid():
                links = form.cleaned_data['categories']
                for link in links:
                    link.categories.add(category)
                    link.save()
                messages.success(request, 'Закладки успешно добавлены в категорию')
        except Exception as e:
            messages.error(request, f'Произошла ошибка при добавлении закладок в категорию: {str(e)}')
        return redirect('links:links-by-category', category_id=category_id)
    else:
        form = AddLinksToCategoryForm(user=request.user, category=category)
        
    context = {
        'title': f'LinkVault - {category.name}',
        'category': category,
        'form': form,
        'actual_year': actual_year,
    }
    return render(request, 'categories/add-links-to-category.html', context=context)


# Удаление самой категории
def delete_category_view(request, category_id):
    category = get_object_or_404(Category, id=category_id, user_id=request.user)
    if request.method == 'POST':
        try:
            category.delete()
            messages.success(request, 'Категория успешно удалена')
        except Exception as e:
            messages.error(request, f'Произошла ошибка при удалении категории: {str(e)}')
    return redirect('links:my-categories')