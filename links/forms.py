from django import forms

from .models import Link, Category


class LinkForm(forms.ModelForm):
    class Meta:
        model = Link
        fields = ['link', 'name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'custom-input', 'placeholder': 'Введите название ссылки'}),
            'link': forms.URLInput(attrs={'class': 'custom-input', 'placeholder': 'Введите URL'}),
            'description': forms.Textarea(attrs={'class': 'custom-textarea', 'placeholder': 'Введите описание (Необязательное поле)', 'rows': 3}),
        }
        
class EditLinkForm(forms.ModelForm):
    class Meta:
        model = Link
        fields = ['link', 'name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'custom-input', 'placeholder': 'Введите название ссылки'}),
            'link': forms.URLInput(attrs={'class': 'custom-input', 'placeholder': 'Введите URL'}),
            'description': forms.Textarea(attrs={'class': 'custom-textarea', 'placeholder': 'Введите описание (Необязательное поле)', 'rows': 3}),
        }
        

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'image']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'custom-input', 'placeholder': 'Введите название категории'}),
        }