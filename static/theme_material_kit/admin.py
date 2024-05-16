from django.contrib import admin
from .models import Car


class CarAdmin(admin.ModelAdmin):
    # Customize the admin form for adding new listings
    fieldsets = (
        (None, {
            'fields': ('brand', 'model', 'price', 'year', 'main_photo', 'photos', 'short_info')
        }),
    )

    # Display these fields in the list view
    list_display = ('brand', 'model', 'price', 'year', 'short_info')

    # Add actions to delete selected cars
    actions = ['delete_selected']


# Register the Car model with your custom admin class
admin.site.register(Car, CarAdmin)
