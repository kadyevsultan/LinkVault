from django.urls import path

from .views import (
    index_view, 
    add_link_view, my_links_view, detail_link_view, delete_link_view, edit_link_view, 
    my_categories_view, add_category_view, links_by_category_view, add_links_to_category_view, edit_category_view, delete_category_view
)

app_name = 'links'

urlpatterns = [
    # Главная страница
    path('', index_view, name='index'),
    # Закладки
    path('my-links', my_links_view, name='my-links'),
    path('link/add-link', add_link_view, name='add-link'),
    path('link/<int:link_id>', detail_link_view, name='detail-link'),
    path('link/<int:link_id>/edit', edit_link_view, name='edit-link'),
    path('link/<int:link_id>/delete', delete_link_view, name='delete-link'),
    # Категории
    path('my-categories', my_categories_view, name='my-categories'),
    path('category/add-category', add_category_view, name='add-category'),
    path('category/<int:category_id>', links_by_category_view, name='links-by-category'),
    path('category/<int:category_id>/add-link', add_links_to_category_view, name='add-links-to-category'),
    path('category/<int:category_id>/edit', edit_category_view, name='edit-category'),
    path('category/<int:category_id>/edit/delete', delete_category_view, name='delete-category'),
]
