from django import forms

from .models import Link, Category
from .services import get_links_by_user_for_category

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
        
        
class AddLinksToCategoryForm(forms.ModelForm):
    class Meta:
        model = Link
        fields = ['categories']
        

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        category = kwargs.pop('category', None)
        super().__init__(*args, **kwargs)
        
        if user and category:
            self.fields['categories'].queryset = get_links_by_user_for_category(user=user, category=category)
            
        
class EditCategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'image']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'custom-input', 'placeholder': 'Введите название категории'}),
        }