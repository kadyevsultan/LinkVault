from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()

class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label='Пароль')
    confirm_password = forms.CharField(widget=forms.PasswordInput, label='Подтверждение пароля')
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        
    def clean_password(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        
        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Пароли не совпадают")
        
        return cleaned_data  
    
    def clean_email(self):
        cleaned_data = super().clean()
        email = cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Пользователь с таким email уже существует")
        return email

class LoginForm(forms.Form):
    username = forms.CharField(label='Логин или Email', widget=forms.TextInput ,max_length=254)
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput)
    
    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')
        
        if not User.objects.filter(username=username).exists() and not User.objects.filter(email=username).exists():
            raise forms.ValidationError("Пользователь с таким логином или email не зарегистрирован")
        
        return cleaned_data


class EditProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email']
        
    def clean_username(self):
        username = self.cleaned_data['username']
        if username == self.instance.username:
            return username
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Пользователь с таким логином уже существует")
        return username
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].widget.attrs['readonly'] = True


class ConfirmEmailForResetPasswordForm(forms.Form):
    email = forms.EmailField(label='Email', widget=forms.EmailInput)
    
    def clean_email(self):
        email = self.cleaned_data['email']
        if not User.objects.filter(email=email).exists():
            raise forms.ValidationError("Пользователь с таким email не зарегистрирован")
        return email
    
    