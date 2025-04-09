from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages

from .forms import RegisterForm, LoginForm

def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            return redirect('accounts:login')
    else:
        form = RegisterForm()
        
    context = {
        'form': form,
        'title': 'LinkVault - Регистрация',
    }
    return render (request, 'accounts/register.html', context=context)


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            
            if '@' in username:
                user = authenticate(request=request, email=username, password=password)
            else:
                user = authenticate(request=request, username=username, password=password)
            
            
            if user is not None:
                login(request, user)
                messages.success(request, 'Вы успешно вошли в свой аккаунт')
                return redirect('links:index')
            else:
                messages.error(request, 'Неправильный логин или пароль')
                form.add_error(None, 'Неправильный логин или пароль')
    else:
        form = LoginForm()
        
    context = {
        'form': form,
        'title': 'LinkVault - Вход',
    }
    
    return render (request, 'accounts/login.html', context=context)


def logout_view(request):
    logout(request=request)
    messages.success(request, 'Вы успешно вышли из своего аккаунта')
    return redirect('links:index')