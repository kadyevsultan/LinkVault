import uuid
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import IntegrityError
from django.core.exceptions import PermissionDenied
from django.http import Http404

from datetime import datetime

from .forms import LinkForm, EditLinkForm, CategoryForm, AddLinksToCategoryForm, EditCategoryForm

from .utils import get_image_from_request, download_favicon, get_image_path_for_session
from .session_keys import SESSION_KEY_CATEGORIES, SESSION_KEY_LINKS
from .services import actual_year
from .services import (
    get_links_by_user, get_last_links, get_categories_by_user, get_links_by_category, get_last_categories,
    create_or_edit_category_from_form,
    delete_link, get_link_by_id, create_or_edit_link_from_form, get_category_by_id_and_user, delete_category,
)

import logging

logger = logging.getLogger(__name__)


""" Главная страница """
def index_view(request):
    context = {
        'title': 'LinkVault - Главная',
        'actual_year': actual_year,
        'user': request.user
    }
    if request.user.is_authenticated:
        context.update({
            'last_links': get_last_links(user=request.user),
            'last_categories': get_last_categories(user=request.user),
            })
    else:
        context.update({
            'last_links': request.session.get(SESSION_KEY_LINKS, [])[:5],
            'last_categories': request.session.get(SESSION_KEY_CATEGORIES, [])[:5],
            })
    return render(request, 'links/index.html', context=context)


""" Закладки """
# Все закладки пользователя
def my_links_view(request):
    if request.user.is_authenticated:
        links = get_links_by_user(request)
    else:
        links = request.session.get(SESSION_KEY_LINKS, [])
    context = {
        'title': 'LinkVault - Мои Закладки',
        'links': links,
        'actual_year': actual_year,
    }
    return render(request, 'links/my-links.html', context=context)


""" Детальная информация о закладке """
def detail_link_view(request, link_id):
    if request.user.is_authenticated:
        link = get_link_by_id(link_id)
        if not link:
            raise Http404("Закладка не найдена")
    else:
        session_links = request.session.get(SESSION_KEY_LINKS, [])
        link = next((l for l in session_links if l['id'] == link_id), None)
        if not link:
            raise Http404("Закладка не найдена")
    context = {
        'title': f'LinkVault - {link["name"] if isinstance(link, dict) else link.name}',
        'link': link,
        'actual_year': actual_year,
    }
    return render(request, 'links/detail-link.html', context=context)


""" Добавление закладки """
def add_link_view(request):
    form = LinkForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        if request.user.is_authenticated:
            try:
                create_or_edit_link_from_form(form=form, user=request.user)
                messages.success(request, 'Ссылка успешно добавлена')
                return redirect('links:my-links')
            except IntegrityError:
                form.add_error("link", "Эта ссылка уже добавлена в ваш список.")
                messages.error(request, 'Эта ссылка уже добавлена в ваш список.')
            except Exception as e:
                logger.error(f'Произошла ошибка при добавлении закладки: {e}')
                messages.error(request, f'Произошла ошибка при добавлении закладки')
        else:
            # Если пользователь не авторизован, сохраняем в сессии
            session_links = request.session.get(SESSION_KEY_LINKS, [])
            new_link_url = form.cleaned_data['link']
            if any(link['link'] == new_link_url for link in session_links):
                form.add_error("link", "Эта ссылка уже добавлена в ваш список.")
                messages.error(request, 'Эта ссылка уже добавлена в ваш список.')
            else:
                # Генерируем уникальный идентификатор
                temp_id = str(uuid.uuid4())
                
                favicon_path = download_favicon(new_link_url)
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
                messages.success(request, 'Ссылка успешно добавлена в ваш список')
                
                return redirect('links:my-links')
                
    elif request.method == 'POST' and form.errors:
        messages.error(request, 'Пожалуйста, исправьте ошибки в форме.')
        
    context = {
        'title': 'LinkVault - Добавить ссылку',
        'form': form,
        'actual_year': actual_year,
    }
    return render (request, 'links/add-link.html', context=context)


""" Удаление закладки """
def delete_link_view(request, link_id):
    if request.user.is_authenticated:
        try:
            delete_link(link_id=link_id, request=request)
            messages.success(request, 'Закладка успешно удалена')
        except PermissionDenied: 
            messages.error(request, 'Вы не можете удалить эту закладку')
        except Exception as e:
            logger.error(e)
            messages.error(request, f'Произошла ошибка при удалении закладки, попробуйте позже.')
    else:
        session_links = request.session.get(SESSION_KEY_LINKS, [])
        for i, link in enumerate(session_links):
            if link['id'] == link_id:
                del session_links[i]
                break
        request.session.modified = True
        messages.success(request, 'Закладка успешно удалена')
    return redirect('links:my-links')


""" Редактирование закладки """
def edit_link_view(request, link_id):
    if request.user.is_authenticated:
        link = get_link_by_id(link_id)
        form = EditLinkForm(request.POST or None, instance=link)
        if request.method == 'POST' and form.is_valid():
            create_or_edit_link_from_form(form=form, user=request.user)
            messages.success(request, 'Ссылка успешно обновлена')
            return redirect('links:detail-link', link_id=link_id)
    else:
        session_links = request.session.get(SESSION_KEY_LINKS, [])
        link = next((l for l in session_links if l['id'] == link_id), None)
        
        if not link:
            messages.error(request, 'Закладка не найдена')
            return redirect('links:my-links')
        if request.method == 'POST':
            form = EditLinkForm(request.POST)
            if form.is_valid():
                link['name'] = form.cleaned_data['name']
                link['link'] = form.cleaned_data['link']
                link['description'] = form.cleaned_data['description']
                request.session.modified = True
                messages.success(request, 'Ссылка успешно обновлена')
                return redirect('links:detail-link', link_id=link_id)
        else:
            form = EditLinkForm(initial=link)
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
        'actual_year': actual_year,
    }
    if request.user.is_authenticated:
        context.update({
            'categories': get_categories_by_user(request),
        })
    else:
        session_categories = request.session.get(SESSION_KEY_CATEGORIES, [])
        context.update({
            'categories': session_categories,
        })
    return render(request, 'categories/categories.html', context=context)


""" Добавление категории """
def add_category_view(request):
    form = CategoryForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():   
        if request.user.is_authenticated:
            try:
                image = get_image_from_request(request=request)
                create_or_edit_category_from_form(form=form, user=request.user, image=image)
                
                messages.success(request, 'Категория успешно добавлена')
                return redirect('links:my-categories')
            except IntegrityError:
                form.add_error("name", "Эта категория уже добавлена в ваш список.")
            except Exception as e:
                logger.error(f'Произошла ошибка при добавлении категории: {e}')
                messages.error(request, f'Произошла ошибка при добавлении категории')
                return redirect('links:my-categories')
        else:
            session_categories = request.session.get(SESSION_KEY_CATEGORIES, [])
            new_category_name = form.cleaned_data['name']
            
            if any(category['name'] == new_category_name for category in session_categories):
                form.add_error("name", "Эта категория уже добавлена в ваш список.")
                messages.error(request, 'Эта категория уже добавлена в ваш список.')
            else:
                # Генерируем уникальный идентификатор
                temp_id = str(uuid.uuid4())
                session_id = request.session.session_key
                
                image = get_image_path_for_session(request=request) or 'defaults/category.png'
                
                new_category_data = {
                    'id': temp_id,
                    'name': new_category_name,
                    'image': image,
                    'session_id': session_id,
                    'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                }
                session_categories.append(new_category_data)
                request.session[SESSION_KEY_CATEGORIES] = session_categories
                request.session.set_expiry(0)
                messages.success(request, 'Категория успешно добавлена в ваш список')
                
            return redirect('links:my-categories')

            
    context = {
        'title': 'LinkVault - Добавить категорию',
        'form': form,
        'actual_year': actual_year,
    }
    return render(request, 'categories/add-category.html', context=context)


""" Страница редактирования категории """
def edit_category_view(request, category_id):
    if request.user.is_authenticated:
        category = get_category_by_id_and_user(category_id=category_id, user_id=request.user)
        form = EditCategoryForm(request.POST or None, instance=category)
        if request.method == 'POST' and form.is_valid():
            try:
                image = get_image_from_request(request=request)
                create_or_edit_category_from_form(form=form, user=request.user, image=image)
                
                messages.success(request, 'Категория успешно обновлена')
                return redirect('links:my-categories')
            except Exception as e:
                logger.error(f'Произошла ошибка при обновлении категории: {e}')
                messages.error(request, f'Произошла ошибка при обновлении категории.')
                return redirect('links:my-categories')
    else:
        session_categories = request.session.get(SESSION_KEY_CATEGORIES, [])
        category = next((category for category in session_categories if category['id'] == category_id), None)
        
        if not category:
            messages.error(request, 'Категория не найдена')
            return redirect('links:my-categories')
        if request.method == 'POST':
            form = EditCategoryForm(request.POST)
            if form.is_valid():
                category['name'] = form.cleaned_data['name']
                category['image'] = get_image_path_for_session(request=request)
                request.session.modified = True
                messages.success(request, 'Категория успешно обновлена')
                return redirect('links:my-categories')
        else:
            form = EditCategoryForm(initial=category)
        
    context = {
        'title': 'LinkVault - Редактировать категорию',
        'form': form,
        'category': category,
        'actual_year': actual_year,
    }
    
    return render(request, 'categories/edit-category.html', context=context)


""" Сама категория и закладки внутри категории """
def links_by_category_view(request, category_id):
    context = {
        'actual_year': actual_year,
    }
    if request.user.is_authenticated:
        category = get_category_by_id_and_user(category_id=category_id, user_id=request.user)
        context.update({
            'links': get_links_by_category(category=category),
            'category': category,
            'title': f'LinkVault - {category.name}',
        })
    else:
        session_categories = request.session.get(SESSION_KEY_CATEGORIES, [])
        category = next((category for category in session_categories if category['id'] == category_id), None)
        
        session_links = request.session.get(SESSION_KEY_LINKS, [])
        category_links = [
            link for link in session_links if 'categories' in link and category_id in link['categories']
        ]
        
        for link in category_links:
            if link.get('favicon_image') and not link['favicon_image'].startswith('/media/'):
                link['favicon_image'] = f'/media/{link["favicon_image"]}'
                
        if not category:
            messages.error(request, 'Категория не найдена')
            return redirect('links:my-categories')
        
        context.update({
            'links': category_links,
            'category': category,
            'title': f'LinkVault - {category['name']}',
        })
    return render(request, 'categories/links-by-category.html', context=context)


""" Добавить закладки в определенную категорию """
def add_links_to_category_view(request, category_id):
    if request.user.is_authenticated:
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
                logger.error(f'Произошла ошибка при добавлении закладок в категорию: {e}')
                messages.error(request, f'Произошла ошибка при добавлении закладок в категорию')
            return redirect('links:links-by-category', category_id=category_id)
    else:
        session_categories = request.session.get(SESSION_KEY_CATEGORIES, [])
        category = next((category for category in session_categories if category['id'] == category_id), None)
        if not category:
            messages.error(request, 'Категория не найдена')
            return redirect('links:my-categories')
        form = AddLinksToCategoryForm(request.POST or None, category=category, request=request)
        
        if request.method == 'POST' and form.is_valid():
            selected_links = form.cleaned_data['categories']
            session_links = request.session.get(SESSION_KEY_LINKS, [])
            for link in session_links:
                if link['id'] in selected_links:
                    if 'categories' not in link:
                        link['categories'] = []
                    if category_id not in link['categories']:
                        link['categories'].append(category_id)
            request.session[SESSION_KEY_LINKS] = session_links
            messages.success(request, 'Закладки успешно добавлены в категорию')
            return redirect('links:links-by-category', category_id=category_id)
        
    context = {
        'title': f'LinkVault - {category["name"] if isinstance(category, dict) else category.name}',
        'category': category,
        'form': form,
        'actual_year': actual_year,
    }
    return render(request, 'categories/add-links-to-category.html', context=context)


""" Удаление самой категории """
def delete_category_view(request, category_id):
    if request.method == 'POST':
        if request.user.is_authenticated:
            try:
                delete_category(request=request, category_id=category_id)
                messages.success(request, 'Категория успешно удалена')
            except Exception as e:
                logger.error(f'Произошла ошибка при удалении категории: {e}')
                messages.error(request, f'Произошла ошибка при удалении категории')
        else:
            session_categories = request.session.get(SESSION_KEY_CATEGORIES, [])
            for i, category in enumerate(session_categories):
                if category['id'] == category_id:
                    del session_categories[i]
                    break
            request.session.modified = True
            messages.success(request, 'Категория успешно удалена')
    return redirect('links:my-categories')


""" Страница о нас """
def about_view(request):
    context = {
        'title': 'LinkVault - О нас',
        'actual_year': actual_year,
    }
    return render(request, 'about.html', context=context)