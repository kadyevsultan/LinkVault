from django import forms

from .models import Link, Category
from .services import get_links_by_user_for_category

from .session_services import SESSION_KEY_CATEGORIES, SESSION_KEY_LINKS

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
    categories = forms.ModelMultipleChoiceField(
        queryset=Link.objects.none(),
        widget=forms.CheckboxSelectMultiple,
        label='Выберите закладки для добавления:',
   )
    
    class Meta:
        model = Link
        fields = ['categories']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        category = kwargs.pop('category', None)
        super().__init__(*args, **kwargs)
        
        if user and category:
            # Для авторизованного пользователя
            self.fields['categories'].queryset = get_links_by_user_for_category(user=user, category=category)
        else:
            self.fields['categories'].choices = []
        
class AddSessionLinksToCategoryForm(forms.ModelForm):
    categories = forms.MultipleChoiceField(
        widget=forms.CheckboxSelectMultiple,
        label='Выберите закладки для добавления:',
        required=False,
    )
    
    class Meta:
        model = Link
        fields = ['categories']
        

    def __init__(self, *args, **kwargs):
        category = kwargs.pop('category', None)
        request = kwargs.pop('request', None) 
        super().__init__(*args, **kwargs)

        if request and category:
            # Для анонимного пользователя (сессия)
            session_links = request.session.get(SESSION_KEY_LINKS, [])
            available_links = [
                (link['id'], link['name']) 
                for link in session_links 
                if category['id'] not in link.get('categories', [])
            ]
            self.fields['categories'].choices = available_links
        else:
            self.fields['categories'].choices = []
            
        
class EditCategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'image']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'custom-input', 'placeholder': 'Введите название категории'}),
        }