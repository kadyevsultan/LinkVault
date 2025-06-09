import logging

from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import IntegrityError
from django.core.exceptions import PermissionDenied
from django.http import Http404

from .forms import (
    LinkForm, EditLinkForm, 
    CategoryForm, AddLinksToCategoryForm, EditCategoryForm, AddSessionLinksToCategoryForm)

from .utils import get_image_from_request

from .services import actual_year
from .services import (
    get_links_by_user, get_last_links, delete_link, get_link_by_id, # Work with links
    get_categories_by_user, get_links_by_category, get_last_categories, # Work with categories
    get_category_by_id_and_user, delete_category, # Work with categories
    create_or_edit_category_from_form, create_or_edit_link_from_form, # Work with forms
)

from .session_services import (
    get_last_session_links, get_links_by_session, get_session_link_by_id,
    add_link_to_session, delete_session_link, edit_session_link,
    get_last_session_categories, get_categories_by_session, get_session_category_by_id,
    add_category_to_session, edit_session_category, get_session_links_by_category,
    get_true_path_for_session_media, add_session_link_to_category, remove_session_link_from_category,
    delete_session_category
)

logger = logging.getLogger(__name__)


""" Главная страница """
def index_view(request):
    show_register_prompt = False
    session_links = get_links_by_session(request)
    if len(session_links) > 0 and not request.user.is_authenticated:
        show_register_prompt = True
    context = {
        'title': 'LinkVault - Главная',
        'actual_year': actual_year,
        'user': request.user,
        'show_register_prompt': show_register_prompt,
    }
    if request.user.is_authenticated:
        context.update({
            'last_links': get_last_links(user=request.user),
            'last_categories': get_last_categories(user=request.user),
            })
    else:
        context.update({
            'last_links': get_last_session_links(request),
            'last_categories': get_last_session_categories(request),
            })
    return render(request, 'links/index.html', context=context)


""" Закладки """
# Все закладки пользователя
def my_links_view(request):
    if request.user.is_authenticated:
        links = get_links_by_user(request)
    else:
        links = get_links_by_session(request)
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
            messages.error(request, 'Закладка не найдена')
            return redirect('links:my-links')
    else:
        link = get_session_link_by_id(request, link_id)
        if not link:
            messages.error(request, 'Закладка не найдена')
            return redirect('links:my-links')
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
            try:
                add_link_to_session(form=form, request=request)
                session_links = get_links_by_session(request)
                if len(session_links) == 1:
                    messages.info(request, 'Вы можете создать аккаунт, чтобы сохранить закладки навсегда.')
                messages.success(request, 'Ссылка успешно добавлена в ваш список')
                return redirect('links:my-links')
            except IntegrityError:
                form.add_error("link", "Эта ссылка уже добавлена в ваш список.")
                messages.error(request, 'Эта ссылка уже добавлена в ваш список.')
            except Exception as e:
                logger.error(f'Произошла ошибка при добавлении закладки в сессию: {e}')
                messages.error(request, f'Произошла ошибка при добавлении закладки в сессию')
                
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
        delete_session_link(link_id=link_id, request=request)
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
        link = get_session_link_by_id(request, link_id)
        
        if not link:
            messages.error(request, 'Закладка не найдена')
            return redirect('links:my-links')
        if request.method == 'POST':
            form = EditLinkForm(request.POST)
            if form.is_valid():
                edit_session_link(form=form, request=request, link=link)
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
        session_categories = get_categories_by_session(request)
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
            session_categories = get_categories_by_session(request)
            new_category_name = form.cleaned_data['name']
            if any(category['name'] == new_category_name for category in session_categories):
                form.add_error("name", "Эта категория уже добавлена в ваш список.")
                messages.error(request, 'Эта категория уже добавлена в ваш список.')
            else:
                add_category_to_session(
                    request=request, new_category_name=new_category_name, session_categories=session_categories
                )
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
        category = get_session_category_by_id(request=request, category_id=category_id)
        
        if not category:
            messages.error(request, 'Категория не найдена')
            return redirect('links:my-categories')
        if request.method == 'POST':
            form = EditCategoryForm(request.POST)
            if form.is_valid():
                edit_session_category(form=form, request=request, category=category)
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
        category = get_session_category_by_id(request=request, category_id=category_id)
        
        category_links = get_session_links_by_category(request=request, category_id=category_id)
        
        get_true_path_for_session_media(category_links=category_links)
                
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
        category = get_session_category_by_id(request=request, category_id=category_id)
        if not category:
            messages.error(request, 'Категория не найдена')
            return redirect('links:my-categories')
        form = AddSessionLinksToCategoryForm(request.POST or None, category=category, request=request)
        
        if request.method == 'POST' and form.is_valid():
            add_session_link_to_category(request=request, form=form, category_id=category_id)
            messages.success(request, 'Закладки успешно добавлены в категорию')
            return redirect('links:links-by-category', category_id=category_id)
        
    context = {
        'title': f'LinkVault - {category["name"] if isinstance(category, dict) else category.name}',
        'category': category,
        'form': form,
        'actual_year': actual_year,
    }
    return render(request, 'categories/add-links-to-category.html', context=context)


""" Удаление закладки из определенной категории """
def delete_link_from_category_view(request, link_id, category_id):
    if request.user.is_authenticated:
        link = get_link_by_id(link_id)
        category = get_category_by_id_and_user(category_id=category_id, user_id=request.user)
        link.categories.remove(category)
        link.save()
        messages.success(request, 'Закладка успешно удалена из категории')
    else:
        session_links = get_links_by_session(request=request)
        remove_session_link_from_category(request=request, links=session_links, category_id=category_id, link_id=link_id)
        messages.success(request, 'Закладка успешно удалена из категории')
    return redirect('links:links-by-category', category_id=category_id)


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
            session_categories = get_categories_by_session(request=request)
            delete_session_category(request=request, category_id=category_id, categories=session_categories)
            messages.success(request, 'Категория успешно удалена')
    return redirect('links:my-categories')


""" Страница о нас """
def about_view(request):
    context = {
        'title': 'LinkVault - О нас',
        'actual_year': actual_year,
    }
    return render(request, 'about.html', context=context)