from django import forms
from django.contrib.auth.models import User

class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label='Пароль')
    confirm_password = forms.CharField(widget=forms.PasswordInput, label='Подтверждение пароля')
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        
        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Пароли не совпадают")
        
        return cleaned_data
    

class LoginForm(forms.Form):
    username = forms.CharField(label='Логин или Email', widget=forms.TextInput ,max_length=254)
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput)


