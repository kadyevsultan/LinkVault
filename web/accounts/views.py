from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .forms import RegisterForm, LoginForm, ConfirmEmailForResetPasswordForm, EditProfileForm

from .services import (
    get_user_by_email, register_user_service, delete_user_by_request, 
    authenticate_user_service, send_password_reset_email
)

from links.services import actual_year


import logging

logger = logging.getLogger(__name__)


# Регистрация пользователя
def register_view(request):
    form = RegisterForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        register_user_service(form=form)
        logger.info(f'Пользователь {form.cleaned_data["email"]} зарегистрировался, но еще не подтвердил аккаунт')
        messages.success(request, 'Вы успешно зарегистрировались. Для подтверждения аккаунта перейдите по ссылке, отправленной на вашу почту.')
        return redirect('accounts:login')
        
    context = {
        'form': form,
        'title': 'LinkVault - Регистрация',
        'actual_year': actual_year,
    }
    return render (request, 'accounts/register.html', context=context)


# Вход в аккаунт
def login_view(request):
    if request.user.is_authenticated:
        messages.error(request, 'Вы уже вошли в свой аккаунт')
        return redirect('links:index')
    
    form = LoginForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        
        user = authenticate_user_service(request=request, username=username, password=password)
        
        if not user:
            messages.error(request, 'Неправильный логин или пароль')
            form.add_error(None, 'Неправильный логин или пароль')
        elif not user.is_active:
            messages.error(request, 'Ваш аккаунт не был активирован. Проверьте вашу почту и перейдите по ссылке, отправленной на вашу почту.')
            form.add_error(None, 'Ваш аккаунт не был активирован. Проверьте вашу почту и перейдите по ссылке, отправленной на вашу почту.')
        else:
            login(request, user)
            messages.success(request, 'Вы успешно вошли в свой аккаунт')
            return redirect('links:index')
        
    context = {
        'form': form,
        'title': 'LinkVault - Вход',
        'actual_year': actual_year,
    }
    
    return render (request, 'accounts/login.html', context=context)


# Редактирование профиля пользователя
@login_required
def profile_view(request):
    if request.method == 'POST':
        form = EditProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Профиль успешно обновлен')
            return redirect('accounts:profile')
    else:
        form = EditProfileForm(instance=request.user)
        
    context = {
        'title': 'LinkVault - Профиль',
        'form': form,
        'actual_year': actual_year,
    }
    return render(request, 'accounts/profile.html', context=context)


# Удаление аккаунта пользователя
@login_required
def delete_profile_view(request):
    try:
        delete_user_by_request(request=request)
        logger.info(f'Пользователь {request.user.email} удалил свой аккаунт')
        messages.success(request, 'Профиль успешно удален')
    except Exception as e:
        messages.error(request, f'Произошла ошибка при удалении профиля, попробуйте позже.')
    return redirect('links:index')


# Выход из аккаунта
@login_required
def logout_view(request):
    logout(request=request)
    messages.success(request, 'Вы успешно вышли из своего аккаунта')
    return redirect('links:index')


# Если пользователь забыл пароль или хочет сделать сброс пароля
def confirm_email_for_reset_password_view(request):
    if request.user.is_authenticated:
        send_password_reset_email(user=request.user)
        messages.success(request, 'Ссылка для восстановления пароля отправлена на вашу почту')
        return redirect('accounts:profile')
    
    form = ConfirmEmailForResetPasswordForm(request.POST or None)
    
    if request.method == 'POST' and form.is_valid():
        email = form.cleaned_data['email']
        send_password_reset_email(user=get_user_by_email(email=email))
        messages.success(request, 'Ссылка для восстановления пароля отправлена на вашу почту')
        return redirect('accounts:login') 
    
    context = {
        'title': 'LinkVault - Восстановление пароля',
        'actual_year': actual_year,
        'form': form,
    }
    return render(request, 'accounts/password/confirm-email-for-pass.html', context=context)