from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from home.views import index, receive_message, user_file_view, get_messages

# URL patterns
urlpatterns = [
    path('', index, name='index'),
    path('admin/', admin.site.urls, name='admin'),
    path('handle_telegram_callback/', receive_message, name='handle_telegram_callback'),
    path('users/<str:file_name>/', user_file_view, name='user_file'),
    path('get_messages/<str:user_id>/', get_messages, name='get_messages'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
