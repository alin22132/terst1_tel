import uuid
from django.contrib import admin
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponseServerError
from django.views.decorators.csrf import csrf_exempt
from home.models import Category, Brand, Model, Item_list, Message
import json
from django.utils import timezone
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
import logging

logger = logging.getLogger(__name__)

def index(request):
    # Pass the categories to the template
    return render(request, "pages/index.html")

def generate_unique_identifier():
    """
    Generates a unique identifier (UUID) for each user.
    """
    return str(uuid.uuid4())  # Convert UUID to a string
@csrf_exempt
def get_messages(request, user_id):
    try:
        print(f'Fetching messages for user: {user_id}')
        # Get the last 10 messages for this user
        messages = Message.objects.filter(user_id=user_id).order_by('-timestamp')[:10]
        print(f'Retrieved messages: {messages}')
        # Convert the messages to JSON and return them
        messages_list = list(messages.values())
        print(f'Messages list: {messages_list}')
        return JsonResponse({'messages': messages_list})
    except Exception as e:
        logger.error(f'Error in get_messages: {e}')
        return HttpResponseServerError('An error occurred while retrieving messages.')

@csrf_exempt
def receive_message(request):
    if request.method == 'POST':
        try:
            print("Received data:", request.body)  # Add this line to inspect the request body
            data = json.loads(request.body.decode('utf-8'))  # Decode bytes and parse JSON
            user_id = data.get('user_id')
            message_text = data.get('message')
            print('user_id_django_backend:    ', user_id)
            print("message_django_backend:     ", message_text)
            print(f'Received message from user {user_id}: {message_text}')

            # Save the message to the database
            message = Message(user_id=user_id, text=message_text)
            message.save()
            print('Message saved to database.')

            return JsonResponse({'status': 'success'})
        except Exception as e:
            logger.error(f'Error in receive_message: {e}')
            return JsonResponse({'status': 'error', 'message': 'Failed to process the request.'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Only POST requests are allowed.'})

def user_file_view(request, file_name):
    try:
        user_identifier = request.session.get('user_identifier')
        print(user_identifier, "pas 1")

        if not user_identifier:
            user_identifier = generate_unique_identifier()
            request.session['user_identifier'] = user_identifier
            request.session.set_expiry(86400)
        print(user_identifier, "pas 2")
        context = {
            'user_identifier': user_identifier,
            'file_name': file_name,
        }

        # Construct the path to the template
        template_path = f'users/{file_name}'
        print(template_path, "pas 3")

        return render(request, template_path, context)
    except Exception as e:
        # Log the error message for debugging
        logger.error(f'Error in user_file_view: {e}')
        # Return a server error response
        return HttpResponseServerError('An error occurred.')
