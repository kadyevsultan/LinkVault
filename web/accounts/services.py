from django.contrib.auth import get_user_model
from django.contrib.auth import login, authenticate, logout


from django_email_verification import send_email, send_password


User = get_user_model()

def get_user_by_email(email):
    """ Получение пользователя по email """
    try:
        return User.objects.get(email=email)
    except User.DoesNotExist:
        return None
    
    
def register_user_service(form):
    """ Регистрация пользователя """
    user = form.save(commit=False)
    user.set_password(form.cleaned_data['password'])
    user.is_active = False
    return send_email(user=user)


def authenticate_user_service(request, username, password, **kwargs):
    """ Аутентификация пользователя """
    try:
        return authenticate(request=request, username=username, password=password)
    except User.DoesNotExist:
        return None


def delete_user_by_request(request):
    """ Удаление пользователя """
    return request.user.delete()


def send_password_reset_email(user):
    """ Отправка ссылки для восстановления пароля """
    return send_password(user=user)