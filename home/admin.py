from django.contrib import admin

from home.models import Category, Brand, Model, Item_list

admin.site.register(Category)
admin.site.register(Brand)
admin.site.register(Model)
admin.site.register(Item_list)

