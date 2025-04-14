from django.contrib import admin

from .models import Link, Category

admin.site.register(Link)
admin.site.register(Category)
admin.site.register(Link.categories.through)
