import os
import requests

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import IntegrityError
from django.contrib.auth.decorators import login_required
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage

from linkvault import settings

from .forms import LinkForm, EditLinkForm, CategoryForm
from .models import Link, Category

from .services import actual_year
from .services import get_links_by_user, get_last_links, get_categories_by_user


def index_view(request):
    context = {
        'title': 'LinkVault - Главная',
        'actual_year': actual_year,
        'last_links': get_last_links(user=request.user),
    }
    return render(request, 'links/index.html', context=context)


def my_links_view(request):
    links = get_links_by_user(request)
    context = {
        'title': 'LinkVault - Мои Закладки',
        'links': links,
    }
    return render(request, 'links/my-links.html', context=context)


def detail_link_view(request, link_id):
    link = get_object_or_404(Link, id=link_id)
    context = {
        'title': f'LinkVault - {link.name}',
        'link': link,
    }
    return render(request, 'links/detail-link.html', context=context)


def delete_link_view(request, link_id):
    link = get_object_or_404(Link, id=link_id)
    try:
        link.delete()
        messages.success(request, 'Закладка успешно удалена')
    except:
        messages.error(request, 'Произошла ошибка при удалении закладки, попробуйте позже.')
    return redirect('links:my-links')


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
    }
    return render (request, 'links/add-link.html', context=context)

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
    }
    return render (request, 'links/edit-link.html', context=context)


# КАТЕГОРИИ
def my_categories_view(request):
    context = {
        'title': 'LinkVault - Мои Категории',
        'categories': get_categories_by_user(request),
    }
    return render(request, 'categories/categories.html', context=context)


@login_required
def add_category_view(request):
    if request.method == 'POST':   
        form = CategoryForm(request.POST)
        if form.is_valid():
            try:
                category = form.save(commit=False)
                category.user_id = request.user
                
                # Если пользователь добавил свою картинку
                if 'image_file' in request.FILES:
                    category.image = request.FILES['image_file']
                
                # Если пользователь выбрал 1 из предложенных img
                elif request.POST['image_url']:
                    # Если пользователь выбрал 1 из предложенных img
                    image_url = request.POST['image_url']
                    filename = os.path.basename(image_url)
                    media_path = os.path.join('category_images', filename)
                    full_path = os.path.join(settings.MEDIA_ROOT, media_path)
                    
                    # Скачиваем картинку если она ещё не скачана
                    if not os.path.exists(full_path):
                        response = requests.get(image_url)
                        if response.status_code == 200:
                            default_storage.save(media_path, ContentFile(response.content))
                            
                    category.image = media_path
                
                category.save()
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
    }
    return render(request, 'categories/add-category.html', context=context)


# def detail_category_view(request, category_id):
#     category = get_object_or_404(Category, id=category_id)
#     context = {
#         'title': f'LinkVault - {category.name}',
#         'category': category,
#     }
#     return render(request, 'categories/detail-category.html', context=context)