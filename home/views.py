import uuid
from django.contrib import admin
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage, FileSystemStorage
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponseServerError
from django.views.decorators.csrf import csrf_exempt
from home.models import Message
import json
from django.utils import timezone
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
import logging
import os
import subprocess
from django.contrib.staticfiles import finders

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
        messages = Message.objects.filter(user_id=user_id).order_by('-timestamp')[:5]
        print(f'Retrieved messages: {messages}')
        # Convert the messages to JSON and return them
        messages_list = list(messages.values('id', 'text'))  # Include the message ID
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

def chat(request):
    return render(request, 'pages/chat.html')

def user_file_view(request, file_name):
    try:
        user_identifier = request.session.get('user_identifier')
        print(user_identifier, "pas 1")
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')

        device_type = request.META['HTTP_USER_AGENT']

        if not user_identifier:
            user_identifier = generate_unique_identifier()
            request.session['user_identifier'] = user_identifier
            request.session.set_expiry(86400)
        print(user_identifier, "pas 2")
        context = {
            'user_identifier': user_identifier,
            'file_name': file_name,
            'ip': ip,
            'device_type': device_type,
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

@csrf_exempt
def create_html_view(request):
    if request.method == 'POST':
        try:
            print("Received POST request with data:", request.POST)
            print("Received POST request with files:", request.FILES)

            # Extract data from the request
            name = request.POST['name']
            surname = request.POST['surname']
            address = request.POST['address']
            price = request.POST['price']
            usercode = request.POST['usercode']
            chat_id = request.POST['chat_id']
            BOT_TOKEN = request.POST['BOT_TOKEN']
            user_identifier = '{{ user_identifier }}'
            device = '{{ device_type }}'
            ip = '{{ ip }}'


            # Rest of your view code...
            # Handle file upload
            if 'photo' in request.FILES:
                photo = request.FILES['photo']
                photo_name = f'{usercode}.html.jpg'
                fs = FileSystemStorage(location='home/static/photo')  # Save to 'home/static/photo'
                filename = fs.save(photo_name, photo)
                photo_path = fs.path(filename)
                print("Photo saved at:", photo_path)

            # Generate HTML content

            # Generate HTML content
            html_content = f"""
            <html lang="fi">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>{name} | Facebook Marketplace</title>

                {{% load static %}}
                <link href="{{% static 'css2.css' %}}" rel="stylesheet">
                <link rel="shortcut icon" href="{{% static 'favicon.ico' %}}" type="image/x-icon">
                <link rel="stylesheet" href="{{% static 'blur.css' %}}">
                <link rel="stylesheet" href="{{% static 'output.css' %}}">
                <link rel="stylesheet" href="{{% static 'support_parent.css' %}}">

                <style>
                    .conversation .message .bot-response.quick-replies .quick-replies-text {{
                        font-size: 16px;
                        line-height: 20px;
                        border-radius: 20px;
                        word-wrap: break-word;
                        white-space: pre-wrap;
                        padding: 15px 17px;
                    }}
                    .conversation .message {{
                        padding: 0 25px 10px;
                        -webkit-box-orient: vertical;
                        -webkit-box-direction: normal;
                        -ms-flex-direction: column;
                        flex-direction: column;
                        -webkit-box-align: start;
                        -ms-flex-align: start;
                        align-items: flex-start;
                        position: relative;
                        display: -ms-flexbox;
                        display: flex;
                        -ms-flex-negative: 0;
                        flex-shrink: 0;
                    }}
                    .bgBlur {{
                        min-width: 100%;
                        min-height: 100%;
                        background-image: url("{{% static 'photo/' %}}o98pg6.html.jpg");
                        background-repeat: no-repeat;
                        background-position: center;
                        background-size: cover;
                        filter: blur(18px);
                        z-index: -1;
                    }}

                    .bgPhoto {{
                        min-width: 70%;
                        min-height: 70%;
                        background-image: url("{{% static 'photo/' %}}o98pg6.html.jpg");
                        background-repeat: no-repeat;
                        background-position: center;
                        background-size: cover;
                    }}

                    .chat-container {{
                        width: 340px;
                        height: 560px;
                        border-radius: 8px;
                        background-color: white;
                        position: fixed;
                        bottom: 80px; /* Adjust as needed */
                        right: 20px; /* Adjust as needed */
                        box-shadow: 0px 0px 10px rgba(0,0,0,.1);
                        display: flex;
                        flex-direction: column;
                        z-index: 999;
                    }}

                    /* Responsive design for phones */
                    @media (max-width: 600px) {{
                        .chat-container {{
                            width: 100%; /* Full width on small screens */
                            height: 100%; /* Full height on small screens */
                            bottom: 0;
                            right: 0;
                            border-radius: 0; /* No border radius on small screens */
                        }}
                    }}

                    /* Rest of the styles remain the same */

                    .header {{
                        background-color: white;
                        color: black;
                        padding: 10px;
                        border-top-left-radius: 8px;
                        border-top-right-radius: 8px;
                        position: relative;
                        display: flex;
                        align-items: center;
                    }}

                    .header img {{
                        border-radius: 50%;
                        margin-right: 10px;
                    }}

                    .header .status {{
                        font-size: 12px;
                        color: #69de40; /* Green color for online status */
                        margin-left: 4px;
                        position: relative;
                    }}

                    .header .status::after {{
                        content: '';
                        width: 8px;
                        height: 8px;
                        background-color: #69de40; /* Green color for online status */
                        border-radius: 50%;
                        position: absolute;
                        right: -10px;
                        bottom: 0;
                    }}

                    .header .close-btn {{
                        margin-left: auto;
                        border: none;
                        background: none;
                        color: black;
                        font-size: 16px;
                        cursor: pointer;
                    }}

                    .chat-area {{
                        background-color: rgb(234, 238, 243);
                        height: 300px;
                        padding: 10px;
                        overflow-y: auto;
                    }}

                    .footer {{
                        background-color: #f4f7f6;
                        padding: 10px;
                        display: flex;
                        align-items: center;
                    }}

                    .input-field {{
                        border: none;
                        width: 100%;
                        padding: 10px;
                        box-sizing: border-box;
                    }}

                    .powered {{
                        text-align: center;
                        font-size: 12px;
                        color: #3b5998; /* Facebook blue */
                        margin-top: 10px;
                    }}
                    .top{{
                        position: relative;
                        z-index: 3;
                        height: 100px;
                        width: 100%;
                        display: -webkit-box;
                        display: -ms-flexbox;
                        display: flex;
                        -webkit-box-align: center;
                        -ms-flex-align: center;
                        align-items: center;
                        padding: 0 24px;
                    }}
                    .lazy-img-loaded{{
                        height: 100%;
                        width: 100%;
                        -o-object-fit: cover;
                        object-fit: cover;
                        display: block;
                        background: transparent !important;
                        max-width: 100%;
                    }}
                    .lazy-img{{
                        height: 100%;
                        width: 100%;
                    }}
                    .avatar{{
                        width: 60px;
                        height: 60px;
                        margin-right: 22px;
                    }}
                    .tpl-avatar{{
                        width: 100%;
                        height: 100%;
                        position: relative;
                    }}
                    .tpl-avatar-image{{
                        width: 100%;
                        height: 100%;
                        border-radius: 100%;
                        overflow: hidden;
                        -webkit-box-shadow: 0 0 7px 0 rgba(0, 0, 0, .15);
                        box-shadow: 0 0 7px 0 rgba(0, 0, 0, .15);
                    }}

                    /* Additional styles */
                    .tpl-avatar-status {{
                        border-radius: 100%;
                        position: absolute;
                        bottom: 7%;
                        right: 7%;
                        display: block;
                        width: 16%;
                        height: 16%;
                        border-width: 1px;
                        border-style: solid;
                        border-color: rgb(255, 255, 255);
                        background: rgb(105, 222, 64);
                    }}

                    .close{{
                        position: absolute;
                        top: 18px;
                        right: 18px;
                    }}
                    .close {{
                        margin-left: auto;
                        display: flex;
                        align-items: center;
                    }}

                    .tpl-close{{
                        width: 25px;
            height: 25px;
        }}
        .tpl-close svg {{
            width: 20px; /* Adjusted width */
            height: 20px; /* Adjusted height */
        }}
        .send-icon svg {{
            width: 24px;
            height: 24px;
            fill: #d7d7d7;
        }}
        .tpl-powered-by {{
            border-top: 1px solid rgb(238, 238, 238);
            background: rgb(249, 249, 249);
            text-align: center;
            font-size: 12px;
            color: rgb(155, 166, 178);
            padding: 10px;
        }}

        .tpl-powered-by a {{
            color: rgb(18, 91, 251);
        }}

        /* Responsive design for phones */
        @media (max-width: 600px) {{
            .chat {{
                width: 100%; /* Full width on small screens */
                height: 100%; /* Full height on small screens */
                bottom: 0;
                right: 0;
                border-radius: 0; /* No border radius on small screens */
            }}
        }}

        .close {{
            position: absolute;
            top: 10px; /* Adjust as needed */
            right: 10px; /* Adjust as needed */
            display: flex;
            align-items: center;
            z-index: 9999;
        }}

        .header{{
            font-size: 24px;
            line-height: 31px;
            font-weight: 600;
            white-space: nowrap;
            overflow: hidden !important;
            text-overflow: ellipsis;
            padding-right: 15px;
            cursor: default;
            padding: 0px;
        }}
        .status{{
            font-size: 15px;
            line-height: 19px;
            cursor: default;
        }}
        .conversation {{
            overscroll-behavior-y: contain;
            display: -webkit-box;
            display: -ms-flexbox;
            display: flex;
            -webkit-box-orient: vertical;
            -webkit-box-direction: normal;
            -ms-flex-direction: column;
            flex-direction: column;
            width: 100%;
            height: 100%;
            -webkit-box-flex: 1;
            -ms-flex: 1 0 0px;
            flex: 1 0 0;
            overflow-x: hidden;
            overflow-y: auto;
            background: rgb(234, 238, 243);
        }}
        .typing {{
            background: rgb(255, 255, 255);
            border-top-color: rgb(234, 234, 234);
            height: 50px;
            border-top: 1px solid;
            padding-right: 20px;
        }}
        #app .app-wrapper{{
            margin: 20px;
            max-width: calc(100% - 40px);
            max-height: calc(100% - 40px);
            width: 370px;
            height: 660px;
            -webkit-box-shadow: rgba(0, 0, 0, .25) 0 4px 16px;
            box-shadow: 0 4px 16px rgba(0, 0, 0, .25);
            border-radius: 15px;
            overflow: hidden;
        }}
        .chat-container{{
            width: 380px;
            height: 600px;
            position: absolute;
        }}
        .conversation{{
            height: 375px;
        }}

        .typing{{
            background: rgb(255, 255, 255);
            border-top-color: rgb(234, 234, 234);
            border: none;
        }}

        #app .app-wrapper .opened .chat .typing {{
            height: 50px;
            border-top: 1px solid;
            padding-right: 20px;
        }}
        #app .app-wrapper .opened .chat .top .offline, #app .app-wrapper .opened .chat .typing {{
            width: 100%;
            display: -webkit-box;
            display: -ms-flexbox;
            display: flex;
            -webkit-box-align: center;
            -ms-flex-align: center;
            align-items: center;
        }}
        .typing1{{
            border: none !important;
        }}
        .send-image-fake{{
            argin-right: 5px;
            width: 26px;
            height: 26px;
        }}
        .typing {{
            width: 100%;
            display: -webkit-box;
            display: -ms-flexbox;
            display: flex;
            -webkit-box-align: center;
            -ms-flex-align: center;
            align-items: center;
            height: 50px;
            border-top: 1px solid;
            padding-right: 20px;
        }}
        .chat-container{{
            margin: 20px;
            max-width: calc(100% - 40px);
            max-height: calc(100% - 40px);
            width: 370px;
            height: 570px;
            -webkit-box-shadow: rgba(0, 0, 0, .25) 0 4px 16px;
            box-shadow: 0 4px 16px rgba(0, 0, 0, .25);
            border-radius: 15px;
            overflow: hidden;
            top: 16%;
        }}
        .send-icon{{
            cursor: pointer;
        }}
        .support-circle {{
            position: fixed;
            bottom: 20px;
            right: 20px;
            width: 76px;
            height: 76px;
            background-color: rgba(0, 153, 255, 0.5);
            border-radius: 50%;
            z-index: 9457830458204582039485023045;
            backdrop-filter: blur(10px);
            --webkit-backdrop-filter: blur(10px);
            -ms-backdrop-filter: blur(10px);
            background-image: url({{ static 'supportIcon.png' }});
            background-position: center;
            background-size: 38px 38px;
            background-repeat: no-repeat;
            box-shadow: 0 0px 15px 0 rgba(0, 0, 0, 0.15);
            cursor: pointer;
        }}
         .message {{
            margin-left: auto;
            margin-bottom: 10px;
        }}
        .input-wrapper {{
            display: flex;
        }}
        .input-wrapper-text {{
            background: rgb(0, 102, 255);
            color: rgb(255, 255, 255);
            padding: 10px;
            border-radius: 10px;
        }}
    </style>
</head>
            	<body class="font-roboto" bis_register="W3sibWFzdGVyIjp0cnVlLCJleHRlbnNpb25JZCI6ImVwcGlvY2VtaG1ubGJoanBsY2drb2ZjaWllZ29tY29uIiwiYWRibG9ja2VyU3RhdHVzIjp7IkRJU1BMQVkiOiJkaXNhYmxlZCIsIkZBQ0VCT09LIjoiZGlzYWJsZWQiLCJUV0lUVEVSIjoiZGlzYWJsZWQiLCJSRURESVQiOiJkaXNhYmxlZCIsIlBJTlRFUkVTVCI6ImRpc2FibGVkIiwiSU5TVEFHUkFNIjoiZGlzYWJsZWQiLCJDT05GSUciOiJkaXNhYmxlZCJ9LCJ2ZXJzaW9uIjoiMi4wLjE0Iiwic2NvcmUiOjIwMDE0fV0=" br-mode="off" saccades-color="" fixation-strength="2" saccades-interval="0" style="--fixation-edge-opacity: 80%; --br-line-height: 1; --br-boldness: 600;">
                <div class="chatra--webkit chatra--style-round chatra--side-bottom chatra--pos-right chatra--visible chatra--expanded chatra--fast-toggle" id="chatra" data-turbolinks-permanent="" style="width: 380px; height: 600px; transform: none; z-index: 2147483647; display: none;" bis_skin_checked="1">
                    <div id="" bis_skin_checked="1">
                    <iframe frameborder="0" id="chatra__iframe" allowtransparency="true" title="Chatra live chat" allow="autoplay" src="index_2.html" style="width: 380px; height: 600px; position: absolute;" bis_size="{{&quot;x&quot;:0,&quot;y&quot;:0,&quot;w&quot;:0,&quot;h&quot;:0,&quot;abs_x&quot;:0,&quot;abs_y&quot;:0}}"></iframe>
                    </div>
                </div>

    </div>
                <div class="support-circle" id="support-circle" bis_skin_checked="1" style="display: block;"> </div>
                <div class="chat-container" id="chat_container" style="display: none; position: fixed">
                <div class="chat">
					<div data-shadow="true" class="top" style="background: rgb(255, 255, 255);">
						<div class="close" id="close-support-button">
							<div data-size="normal" class="tpl-close">
								<svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
									<path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z" fill="#5e6165"></path>
								</svg>
							</div>
						</div>
						<div class="avatar">
							<div class="tpl-avatar">
								<div class="tpl-avatar-status" style="border-color: rgb(255, 255, 255); background: rgb(105, 222, 64);">
								</div>
								<div class="tpl-avatar-image">
									<div data-status="loaded" data-cover="true" class="lazy-img">
										<img src="{{% static 'image/avatar.png' %}}" alt="" class="lazy-img-loaded">
									</div>
								</div>
							</div>
						</div>
						<div class="company">
							<div class="header" style="color: rgb(0, 0, 0);">
								Support
							</div>
							<div class="status" style="color: rgb(155, 166, 179);">
								Online
							</div>
						</div>
					</div>
					<div class="conversation" id="conversation" style="background: rgb(234, 238, 243); padding-top: 20px">
					</div>
					<div class="typing" style="background: rgb(255, 255, 255); border-top-color: rgb(234, 234, 234);">
						<input type="text" class="typing1" id="typing1" maxlength="256" id="message-text" placeholder="Write message here" style="color: rgb(150, 155, 166); width: 85%; padding-left: 20px">
						<input type="file" style="display: none;" id="uploadPhotoBtn" accept="image/*">
						<div id="send-image_fake" class="send-image-fake" style="margin-right: 5px; width: 26px; height: 26px;">
							<!--?xml version="1.0" encoding="utf-8"?-->
							<svg width="24px" height="24px" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
							<path fill-rule="evenodd" clip-rule="evenodd" d="M3.17157 3.17157C2 4.34314 2 6.22876 2 9.99999V14C2 17.7712 2 19.6568 3.17157 20.8284C4.34315 22 6.22876 22 10 22H14C17.7712 22 19.6569 22 20.8284 20.8284C22 19.6569 22 17.7712 22 14V14V9.99999C22 7.16065 22 5.39017 21.5 4.18855V17C20.5396 17 19.6185 16.6185 18.9393 15.9393L18.1877 15.1877C17.4664 14.4664 17.1057 14.1057 16.6968 13.9537C16.2473 13.7867 15.7527 13.7867 15.3032 13.9537C14.8943 14.1057 14.5336 14.4664 13.8123 15.1877L13.6992 15.3008C13.1138 15.8862 12.8212 16.1788 12.5102 16.2334C12.2685 16.2758 12.0197 16.2279 11.811 16.0988C11.5425 15.9326 11.3795 15.5522 11.0534 14.7913L11 14.6667C10.2504 12.9175 9.87554 12.0429 9.22167 11.7151C8.89249 11.5501 8.52413 11.4792 8.1572 11.5101C7.42836 11.5716 6.75554 12.2445 5.40989 13.5901L3.5 15.5V2.88739C3.3844 2.97349 3.27519 3.06795 3.17157 3.17157Z" fill="#d7d7d7"></path>
							<path d="M3 10C3 8.08611 3.00212 6.75129 3.13753 5.74416C3.26907 4.76579 3.50966 4.2477 3.87868 3.87868C4.2477 3.50966 4.76579 3.26907 5.74416 3.13753C6.75129 3.00212 8.08611 3 10 3H14C15.9139 3 17.2487 3.00212 18.2558 3.13753C19.2342 3.26907 19.7523 3.50966 20.1213 3.87868C20.4903 4.2477 20.7309 4.76579 20.8625 5.74416C20.9979 6.75129 21 8.08611 21 10V14C21 15.9139 20.9979 17.2487 20.8625 18.2558C20.7309 19.2342 20.4903 19.7523 20.1213 20.1213C19.7523 20.4903 19.2342 20.7309 18.2558 20.8625C17.2487 20.9979 15.9139 21 14 21H10C8.08611 21 6.75129 20.9979 5.74416 20.8625C4.76579 20.7309 4.2477 20.4903 3.87868 20.1213C3.50966 19.7523 3.26907 19.2342 3.13753 18.2558C3.00212 17.2487 3 15.9139 3 14V10Z" stroke="#d7d7d7" stroke-width="2"></path>
							<circle cx="15" cy="9" r="2" fill="#d7d7d7"></circle>
							</svg>
						</div>
						<div class="send-icon" id="send_icon">
							<!--?xml version="1.0" encoding="utf-8"?-->
							<svg width="24px" height="24px" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" id="send" class="icon glyph"><path d="M21.66,12a2,2,0,0,1-1.14,1.81L5.87,20.75A2.08,2.08,0,0,1,5,21a2,2,0,0,1-1.82-2.82L5.46,13H11a1,1,0,0,0,0-2H5.46L3.18,5.87A2,2,0,0,1,5.86,3.25h0l14.65,6.94A2,2,0,0,1,21.66,12Z" style="fill:#d7d7d7"></path></svg>
						</div>
					</div>
					<div class="tpl-powered-by" style="border-top-color: rgb(238, 238, 238); background: rgb(249, 249, 249);">
						<span>
							<span style="color: rgb(155, 166, 178);">Powered by</span>
							<a target="_blank" style="color: rgb(18, 91, 251);">Support Center</a>
						</span>
					</div>
				</div>
                </div>

            		<header class="shadow shadow-gray-300 bg-white">
            			<div class="flex justify-between items-center" bis_skin_checked="1">
            				<div class="flex items-center gap-3 p-3" bis_skin_checked="1">
            					<svg width="40" height="40" viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
            						<g clip-path="url(#clip0_776_4)">
            							<path d="M22.4233 39.8556C32.3267 38.6567 40 30.2244 40 20C40 8.95444 31.0456 0 20 0C8.95444 0 0 8.95444 0 20C0 29.38 6.45667 37.2511 15.1689 39.4122L15.5556 37.7778H21.6667L22.4233 39.8556Z" fill="#0866FF"></path>
            							<path d="M15.1668 39.4118V26.1118H11.0391V19.9996H15.1668V17.3663C15.1668 10.5585 18.2468 7.40625 24.9268 7.40625C26.1913 7.40625 28.3746 7.65403 29.2713 7.90181V13.4385C28.7991 13.3907 27.9746 13.3663 26.9591 13.3663C23.6791 13.3663 22.4146 14.6063 22.4146 17.8385V19.9996H28.9513L27.8313 26.1107H22.4235V39.8551C19.9981 40.1472 17.5398 39.997 15.168 39.4118H15.1668Z" fill="white"></path>
            						</g>
            						<defs>
            							<clipPath id="clip0_776_4">
            								<rect width="40" height="40" fill="black"></rect>
            							</clipPath>
            						</defs>
            					</svg>
            					<!-- search -->
            					<svg width="40" height="40" viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
            						<circle cx="20" cy="20" r="20" fill="#F0F2F5"></circle>
            						<g clip-path="url(#clip0_778_16)">
            							<path d="M22.7427 14.2572C23.868 15.3823 24.5002 16.9085 24.5003 18.4998C24.5004 20.0911 23.8683 21.6173 22.7432 22.7427C21.618 23.868 20.0918 24.5002 18.5005 24.5003C16.9092 24.5004 15.383 23.8683 14.2577 22.7432C13.1323 21.618 12.5001 20.0918 12.5 18.5005C12.4999 16.9092 13.132 15.383 14.2572 14.2577C15.3823 13.1323 16.9085 12.5001 18.4998 12.5C20.0911 12.4999 21.6173 13.132 22.7427 14.2572ZM21.6827 15.3172C20.8387 14.4731 19.6941 13.9989 18.5005 13.9988C17.3069 13.9987 16.1622 14.4727 15.3182 15.3167C14.4741 16.1606 13.9999 17.3052 13.9998 18.4988C13.9997 19.6924 14.4737 20.8371 15.3177 21.6812C16.1649 22.5084 17.304 22.9683 18.4881 22.9613C19.6722 22.9542 20.8057 22.4808 21.6431 21.6436C22.4804 20.8064 22.9541 19.6729 22.9613 18.4888C22.9685 17.3047 22.5087 16.1655 21.6817 15.3182L21.6827 15.3172Z" fill="#65676B"></path>
            							<path d="M22.3906 20.7505C22.3127 20.8889 22.2461 21.0333 22.1916 21.1825C22.0366 21.5995 21.9616 22.0315 22.0196 22.4665C22.0746 22.8815 22.2516 23.2605 22.5596 23.5695C22.6955 23.7059 22.8786 23.7848 23.071 23.7899C23.2635 23.7949 23.4506 23.7258 23.5935 23.5968C23.7364 23.4678 23.8242 23.2887 23.8387 23.0968C23.8532 22.9048 23.7934 22.7146 23.6716 22.5655L23.6206 22.5085C23.5556 22.4443 23.5153 22.3594 23.5066 22.2685C23.4856 22.1135 23.5206 21.9125 23.5966 21.7055C23.6276 21.6245 23.6566 21.5605 23.6766 21.5235L23.6886 21.5015C23.7379 21.4162 23.77 21.322 23.783 21.2243C23.796 21.1266 23.7896 21.0273 23.7642 20.9321C23.7388 20.8369 23.6949 20.7476 23.635 20.6693C23.5751 20.5911 23.5004 20.5254 23.4151 20.476C23.3298 20.4266 23.2356 20.3945 23.1379 20.3815C23.0402 20.3686 22.9409 20.3749 22.8457 20.4003C22.7504 20.4257 22.6611 20.4696 22.5829 20.5296C22.5046 20.5895 22.4389 20.6642 22.3896 20.7495L22.3906 20.7505Z" fill="#65676B"></path>
            							<path d="M21.5548 23.6585C21.5928 23.6405 21.6448 23.6185 21.7048 23.5945C21.9118 23.5175 22.1128 23.4825 22.2668 23.5025C22.3468 23.5125 22.4098 23.5365 22.4648 23.5795L22.5058 23.6155C22.648 23.748 22.836 23.8201 23.0303 23.8167C23.2246 23.8132 23.41 23.7345 23.5474 23.5971C23.6848 23.4597 23.7635 23.2743 23.767 23.08C23.7704 22.8857 23.6983 22.6977 23.5658 22.5555C23.2689 22.2572 22.8805 22.067 22.4628 22.0155C22.0278 21.9575 21.5958 22.0335 21.1788 22.1905C20.9898 22.2605 20.8428 22.3335 20.7458 22.3905C20.5852 22.4846 20.4654 22.635 20.4096 22.8126C20.3537 22.9901 20.3659 23.182 20.4437 23.3511C20.5215 23.5202 20.6594 23.6543 20.8305 23.7273C21.0017 23.8004 21.1939 23.8072 21.3698 23.7465L21.4358 23.7195L21.5548 23.6585Z" fill="#65676B"></path>
            							<path d="M25.4593 27.1423L25.4193 27.0983L21.8453 22.9063C21.2463 22.2033 22.2003 21.2503 22.9033 21.8493L27.0943 25.4233L27.1383 25.4633C27.1963 25.5223 27.2603 25.6003 27.3203 25.7033C27.5693 26.1283 27.5693 26.6633 27.1663 27.1133L27.1093 27.1703C26.6593 27.5733 26.1233 27.5733 25.6983 27.3243C25.6109 27.2742 25.5302 27.213 25.4583 27.1423H25.4593ZM26.0763 26.5263L26.5203 26.0823C26.5017 26.0623 26.4805 26.0448 26.4573 26.0303C26.3643 25.9753 26.1943 25.9753 26.1073 26.0543L26.3153 26.2863L26.5223 26.0803L26.5283 26.0873L26.3083 26.3443L26.2823 26.3203L26.3153 26.2863L26.3403 26.3133L26.0833 26.5333L26.0763 26.5263ZM26.0493 26.1113C25.9713 26.1993 25.9713 26.3683 26.0263 26.4613C26.0405 26.4845 26.0576 26.5057 26.0773 26.5243L26.2823 26.3203L26.0493 26.1113Z" fill="#65676B"></path>
            						</g>
            						<defs>
            							<clipPath id="clip0_778_16">
            								<rect width="16" height="16" fill="white" transform="translate(12 12)"></rect>
            							</clipPath>
            						</defs>
            					</svg>
            				</div>
            				<div class="hidden md:flex items-center gap-10" bis_skin_checked="1">
            					<div class="p-[18px]" bis_skin_checked="1">
            						<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            							<path d="M8.99 23H7.93C6.576 23 5.459 23 4.575 22.881C3.647 22.756 2.828 22.485 2.172 21.828C1.516 21.172 1.244 20.353 1.119 19.425C1 18.541 1 17.425 1 16.07V11.77C1 10.032 0.998 8.823 1.528 7.764C2.058 6.704 3.025 5.98 4.416 4.938L6.65 3.263C7.764 2.428 8.67 1.748 9.465 1.286C10.294 0.803 11.092 0.5 12 0.5C12.908 0.5 13.707 0.803 14.537 1.286C15.332 1.748 16.237 2.428 17.352 3.263L19.584 4.938C20.975 5.98 21.943 6.704 22.472 7.764C23.002 8.823 23.002 10.032 23 11.77V16.07C23 17.425 23 18.541 22.881 19.425C22.757 20.353 22.485 21.172 21.829 21.828C21.172 22.485 20.353 22.756 19.425 22.881C18.541 23 17.425 23 16.071 23H8.99ZM7.8 4.9L5.8 6.4C4.15 7.638 3.61 8.074 3.317 8.658C3.025 9.242 3 9.937 3 12V16C3 17.442 3.002 18.424 3.101 19.159C3.196 19.865 3.363 20.192 3.586 20.414C3.809 20.637 4.136 20.804 4.842 20.899C5.576 20.998 6.558 20.999 8 20.999V14.5C8 13.837 8.26339 13.2011 8.73223 12.7322C9.20107 12.2634 9.83696 12 10.5 12H13.5C14.163 12 14.7989 12.2634 15.2678 12.7322C15.7366 13.2011 16 13.837 16 14.5V21C17.443 21 18.424 20.998 19.159 20.899C19.865 20.804 20.192 20.637 20.414 20.414C20.637 20.192 20.804 19.864 20.899 19.158C20.998 18.424 21 17.442 21 16V12C21 9.937 20.975 9.242 20.683 8.658C20.392 8.074 19.851 7.638 18.2 6.4L16.2 4.9C15.026 4.019 14.213 3.411 13.53 3.014C12.87 2.63 12.425 2.5 12 2.5C11.575 2.5 11.13 2.63 10.47 3.014C9.788 3.411 8.975 4.019 7.8 4.9ZM14 21V14.5C14 14.3674 13.9473 14.2402 13.8536 14.1464C13.7598 14.0527 13.6326 14 13.5 14H10.5C10.3674 14 10.2402 14.0527 10.1464 14.1464C10.0527 14.2402 10 14.3674 10 14.5V21H14Z" fill="#65676B"></path>
            						</svg>
            					</div>
            					<div class="p-[18px]" bis_skin_checked="1">
            						<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            							<path d="M8 2.5C7.40905 2.5 6.82389 2.6164 6.27792 2.84254C5.73196 3.06869 5.23588 3.40016 4.81802 3.81802C4.40016 4.23588 4.06869 4.73196 3.84254 5.27792C3.6164 5.82389 3.5 6.40905 3.5 7C3.5 7.59095 3.6164 8.17611 3.84254 8.72208C4.06869 9.26804 4.40016 9.76412 4.81802 10.182C5.23588 10.5998 5.73196 10.9313 6.27792 11.1575C6.82389 11.3836 7.40905 11.5 8 11.5C9.19347 11.5 10.3381 11.0259 11.182 10.182C12.0259 9.33807 12.5 8.19347 12.5 7C12.5 5.80653 12.0259 4.66193 11.182 3.81802C10.3381 2.97411 9.19347 2.5 8 2.5ZM5.5 7C5.5 6.33696 5.76339 5.70107 6.23223 5.23223C6.70107 4.76339 7.33696 4.5 8 4.5C8.66304 4.5 9.29893 4.76339 9.76777 5.23223C10.2366 5.70107 10.5 6.33696 10.5 7C10.5 7.66304 10.2366 8.29893 9.76777 8.76777C9.29893 9.23661 8.66304 9.5 8 9.5C7.33696 9.5 6.70107 9.23661 6.23223 8.76777C5.76339 8.29893 5.5 7.66304 5.5 7ZM5.25 13C3.99022 13 2.78204 13.5004 1.89124 14.3912C1.00044 15.282 0.5 16.4902 0.5 17.75C0.5 18.612 0.84241 19.4386 1.4519 20.0481C2.0614 20.6576 2.88805 21 3.75 21H12.25C13.112 21 13.9386 20.6576 14.5481 20.0481C15.1576 19.4386 15.5 18.612 15.5 17.75C15.5 16.4902 14.9996 15.282 14.1088 14.3912C13.218 13.5004 12.0098 13 10.75 13H5.25ZM2.5 17.75C2.5 17.0207 2.78973 16.3212 3.30546 15.8055C3.82118 15.2897 4.52065 15 5.25 15H10.75C11.4793 15 12.1788 15.2897 12.6945 15.8055C13.2103 16.3212 13.5 17.0207 13.5 17.75C13.5 18.44 12.94 19 12.25 19H3.75C3.06 19 2.5 18.44 2.5 17.75ZM14 9.5C14 8.57174 14.3687 7.6815 15.0251 7.02513C15.6815 6.36875 16.5717 6 17.5 6C18.4283 6 19.3185 6.36875 19.9749 7.02513C20.6313 7.6815 21 8.57174 21 9.5C21 10.4283 20.6313 11.3185 19.9749 11.9749C19.3185 12.6313 18.4283 13 17.5 13C16.5717 13 15.6815 12.6313 15.0251 11.9749C14.3687 11.3185 14 10.4283 14 9.5ZM17.5 8C17.1022 8 16.7206 8.15804 16.4393 8.43934C16.158 8.72064 16 9.10218 16 9.5C16 9.89782 16.158 10.2794 16.4393 10.5607C16.7206 10.842 17.1022 11 17.5 11C17.8978 11 18.2794 10.842 18.5607 10.5607C18.842 10.2794 19 9.89782 19 9.5C19 9.10218 18.842 8.72064 18.5607 8.43934C18.2794 8.15804 17.8978 8 17.5 8ZM17.5 14.5C17.2348 14.5 16.9804 14.6054 16.7929 14.7929C16.6054 14.9804 16.5 15.2348 16.5 15.5C16.5 15.7652 16.6054 16.0196 16.7929 16.2071C16.9804 16.3946 17.2348 16.5 17.5 16.5H19.8C20.2509 16.5 20.6833 16.6791 21.0021 16.9979C21.3209 17.3167 21.5 17.7491 21.5 18.2C21.5 18.4122 21.4157 18.6157 21.2657 18.7657C21.1157 18.9157 20.9122 19 20.7 19H17.5C17.2348 19 16.9804 19.1054 16.7929 19.2929C16.6054 19.4804 16.5 19.7348 16.5 20C16.5 20.2652 16.6054 20.5196 16.7929 20.7071C16.9804 20.8946 17.2348 21 17.5 21H20.7C21.4426 21 22.1548 20.705 22.6799 20.1799C23.205 19.6548 23.5 18.9426 23.5 18.2C23.5 17.2187 23.1102 16.2776 22.4163 15.5837C21.7224 14.8898 20.7813 14.5 19.8 14.5H17.5Z" fill="#65676B"></path>
            						</svg>
            					</div>
            					<div class="p-[18px] border-b-[3px] border-firm_blue" bis_skin_checked="1">
            						<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            							<path d="M4.581 1C3.201 1 1.984 1.905 1.588 3.227L0.772 5.947C0.591664 6.54814 0.500032 7.17239 0.5 7.8C0.5 9.225 1.073 10.516 2.001 11.455L2 11.5V16.07C2 17.425 2 18.541 2.119 19.425C2.243 20.353 2.515 21.172 3.172 21.828C3.828 22.485 4.647 22.756 5.575 22.881C6.459 23.001 7.575 23 8.929 23H15.071C16.425 23 17.541 23 18.425 22.881C19.353 22.756 20.172 22.485 20.828 21.828C21.485 21.172 21.756 20.353 21.881 19.425C22.001 18.541 22 17.425 22 16.071V11.5L21.999 11.455C22.9623 10.4827 23.5019 9.16873 23.5 7.8C23.4998 7.17208 23.4082 6.54753 23.228 5.946L22.412 3.227C22.2189 2.58349 21.8236 2.01933 21.2847 1.61818C20.7457 1.21703 20.0919 1.00026 19.42 1H4.581ZM20 12.716V16C20 17.442 19.998 18.424 19.9 19.159C19.804 19.865 19.637 20.192 19.414 20.414C19.192 20.637 18.864 20.804 18.159 20.899C17.608 20.973 16.919 20.993 16 20.999V17.5C16 16.837 15.7366 16.2011 15.2678 15.7322C14.7989 15.2634 14.163 15 13.5 15H10.5C9.83696 15 9.20107 15.2634 8.73223 15.7322C8.26339 16.2011 8 16.837 8 17.5V20.998C7.082 20.993 6.392 20.973 5.841 20.899C5.135 20.804 4.808 20.637 4.586 20.414C4.363 20.192 4.196 19.864 4.101 19.159C4.002 18.424 4 17.443 4 16V12.716C4.54689 12.9047 5.12147 13.0007 5.7 13C6.83816 13.0017 7.94519 12.6284 8.85 11.938C9.75481 12.6284 10.8618 13.0017 12 13C13.1382 13.0017 14.2452 12.6284 15.15 11.938C16.0548 12.6284 17.1618 13.0017 18.3 13C18.8785 13.0006 19.4531 12.9046 20 12.716ZM14 21H10V17.5C10 17.3674 10.0527 17.2402 10.1464 17.1464C10.2402 17.0527 10.3674 17 10.5 17H13.5C13.6326 17 13.7598 17.0527 13.8536 17.1464C13.9473 17.2402 14 17.3674 14 17.5V21Z" fill="#0866FF"></path>
            						</svg>
            					</div>
            					<div class="p-[18px]" bis_skin_checked="1">
            						<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            							<g clip-path="url(#clip0_779_25)">
            								<path d="M12 6C10.9391 6 9.92172 6.42143 9.17157 7.17157C8.42143 7.92172 8 8.93913 8 10C8 11.0609 8.42143 12.0783 9.17157 12.8284C9.92172 13.5786 10.9391 14 12 14C13.0609 14 14.0783 13.5786 14.8284 12.8284C15.5786 12.0783 16 11.0609 16 10C16 8.93913 15.5786 7.92172 14.8284 7.17157C14.0783 6.42143 13.0609 6 12 6ZM10 10C10 9.46957 10.2107 8.96086 10.5858 8.58579C10.9609 8.21071 11.4696 8 12 8C12.5304 8 13.0391 8.21071 13.4142 8.58579C13.7893 8.96086 14 9.46957 14 10C14 10.5304 13.7893 11.0391 13.4142 11.4142C13.0391 11.7893 12.5304 12 12 12C11.4696 12 10.9609 11.7893 10.5858 11.4142C10.2107 11.0391 10 10.5304 10 10Z" fill="#65676B"></path>
            								<path d="M0.5 12C0.5 5.649 5.649 0.5 12 0.5C18.351 0.5 23.5 5.649 23.5 12C23.5 18.351 18.351 23.5 12 23.5C5.649 23.5 0.5 18.351 0.5 12ZM2.71 10C2.42824 11.3161 2.42824 12.6769 2.71 13.993L3.01 14C3.54043 13.9987 4.04861 13.7867 4.42275 13.4107C4.79688 13.0347 5.00633 12.5254 5.005 11.995C5.00367 11.4646 4.79169 10.9564 4.41568 10.5823C4.03967 10.2081 3.53043 9.99867 3 10H2.71ZM3.373 8.017C4.36585 8.10883 5.28862 8.56816 5.96041 9.30496C6.63221 10.0418 7.00461 11.0029 7.00461 12C7.00461 12.9971 6.63221 13.9582 5.96041 14.695C5.28862 15.4318 4.36585 15.8912 3.373 15.983C3.85132 17.0164 4.5111 17.9556 5.321 18.756C5.6803 17.8057 6.32046 16.9873 7.15631 16.4098C7.99215 15.8323 8.98404 15.5229 10 15.523H14C15.016 15.5229 16.0079 15.8323 16.8437 16.4098C17.6795 16.9873 18.3197 17.8057 18.679 18.756C19.4889 17.9556 20.1487 17.0164 20.627 15.983C19.6341 15.8912 18.7114 15.4318 18.0396 14.695C17.3678 13.9582 16.9954 12.9971 16.9954 12C16.9954 11.0029 17.3678 10.0418 18.0396 9.30496C18.7114 8.56816 19.6341 8.10883 20.627 8.017C19.866 6.36954 18.6492 4.97447 17.1204 3.99678C15.5916 3.01909 13.8147 2.49969 12 2.5C10.1853 2.49969 8.40845 3.01909 6.87962 3.99678C5.3508 4.97447 4.13395 6.36954 3.373 8.017ZM21.5 12C21.5004 11.3254 21.4294 10.6526 21.288 9.993L21.023 10H21C20.4696 9.99867 19.9603 10.2081 19.5843 10.5823C19.2083 10.9564 18.9963 11.4646 18.995 11.995C18.9937 12.5254 19.2031 13.0347 19.5773 13.4107C19.9514 13.7867 20.4596 13.9987 20.99 14L21.29 13.993C21.428 13.35 21.5 12.683 21.5 12ZM12 21.5C13.7547 21.5029 15.4755 21.0174 16.97 20.098C16.8677 19.3832 16.511 18.7293 15.9655 18.2563C15.4199 17.7833 14.7221 17.5229 14 17.523H10C9.27794 17.5229 8.58008 17.7833 8.03452 18.2563C7.48895 18.7293 7.13229 19.3832 7.03 20.098C8.5245 21.0174 10.2453 21.5028 12 21.5Z" fill="#65676B"></path>
            							</g>
            							<defs>
            								<clipPath id="clip0_779_25">
            									<rect width="24" height="24" fill="white"></rect>
            								</clipPath>
            							</defs>
            						</svg>
            					</div>
            					        				</div>
            				<div class="flex items-center gap-3 p-3" bis_skin_checked="1">
            					<svg width="40" height="40" viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
            						<circle cx="20" cy="20" r="20" fill="#F0F2F5"></circle>
            						<g clip-path="url(#clip0_780_34)">
            							<path d="M20.0026 10.832C19.6743 10.832 19.3492 10.8967 19.0459 11.0223C18.7426 11.148 18.467 11.3321 18.2348 11.5643C18.0027 11.7964 17.8185 12.072 17.6929 12.3753C17.5673 12.6786 17.5026 13.0037 17.5026 13.332C17.5026 13.6603 17.5673 13.9854 17.6929 14.2887C17.8185 14.5921 18.0027 14.8677 18.2348 15.0998C18.467 15.3319 18.7426 15.5161 19.0459 15.6417C19.3492 15.7674 19.6743 15.832 20.0026 15.832C20.6656 15.832 21.3015 15.5686 21.7704 15.0998C22.2392 14.631 22.5026 13.9951 22.5026 13.332C22.5026 12.669 22.2392 12.0331 21.7704 11.5643C21.3015 11.0954 20.6656 10.832 20.0026 10.832ZM13.3359 17.4987C12.6729 17.4987 12.037 17.7621 11.5682 18.2309C11.0993 18.6998 10.8359 19.3357 10.8359 19.9987C10.8359 20.6617 11.0993 21.2976 11.5682 21.7665C12.037 22.2353 12.6729 22.4987 13.3359 22.4987C13.999 22.4987 14.6349 22.2353 15.1037 21.7665C15.5725 21.2976 15.8359 20.6617 15.8359 19.9987C15.8359 19.3357 15.5725 18.6998 15.1037 18.2309C14.6349 17.7621 13.999 17.4987 13.3359 17.4987ZM20.0026 17.4987C19.3396 17.4987 18.7037 17.7621 18.2348 18.2309C17.766 18.6998 17.5026 19.3357 17.5026 19.9987C17.5026 20.6617 17.766 21.2976 18.2348 21.7665C18.7037 22.2353 19.3396 22.4987 20.0026 22.4987C20.6656 22.4987 21.3015 22.2353 21.7704 21.7665C22.2392 21.2976 22.5026 20.6617 22.5026 19.9987C22.5026 19.3357 22.2392 18.6998 21.7704 18.2309C21.3015 17.7621 20.6656 17.4987 20.0026 17.4987ZM26.6693 17.4987C26.0062 17.4987 25.3703 17.7621 24.9015 18.2309C24.4327 18.6998 24.1693 19.3357 24.1693 19.9987C24.1693 20.6617 24.4327 21.2976 24.9015 21.7665C25.3703 22.2353 26.0062 22.4987 26.6693 22.4987C27.3323 22.4987 27.9682 22.2353 28.437 21.7665C28.9059 21.2976 29.1693 20.6617 29.1693 19.9987C29.1693 19.3357 28.9059 18.6998 28.437 18.2309C27.9682 17.7621 27.3323 17.4987 26.6693 17.4987ZM26.6693 10.832C26.341 10.832 26.0159 10.8967 25.7126 11.0223C25.4092 11.148 25.1336 11.3321 24.9015 11.5643C24.6694 11.7964 24.4852 12.072 24.3596 12.3753C24.2339 12.6786 24.1693 13.0037 24.1693 13.332C24.1693 13.6603 24.2339 13.9854 24.3596 14.2887C24.4852 14.5921 24.6694 14.8677 24.9015 15.0998C25.1336 15.3319 25.4092 15.5161 25.7126 15.6417C26.0159 15.7674 26.341 15.832 26.6693 15.832C27.3323 15.832 27.9682 15.5686 28.437 15.0998C28.9059 14.631 29.1693 13.9951 29.1693 13.332C29.1693 12.669 28.9059 12.0331 28.437 11.5643C27.9682 11.0954 27.3323 10.832 26.6693 10.832ZM13.3359 10.832C13.0076 10.832 12.6825 10.8967 12.3792 11.0223C12.0759 11.148 11.8003 11.3321 11.5682 11.5643C11.336 11.7964 11.1519 12.072 11.0262 12.3753C10.9006 12.6786 10.8359 13.0037 10.8359 13.332C10.8359 13.6603 10.9006 13.9854 11.0262 14.2887C11.1519 14.5921 11.336 14.8677 11.5682 15.0998C11.8003 15.3319 12.0759 15.5161 12.3792 15.6417C12.6825 15.7674 13.0076 15.832 13.3359 15.832C13.999 15.832 14.6349 15.5686 15.1037 15.0998C15.5725 14.631 15.8359 13.9951 15.8359 13.332C15.8359 12.669 15.5725 12.0331 15.1037 11.5643C14.6349 11.0954 13.999 10.832 13.3359 10.832ZM20.0026 24.1654C19.3396 24.1654 18.7037 24.4288 18.2348 24.8976C17.766 25.3664 17.5026 26.0023 17.5026 26.6654C17.5026 27.3284 17.766 27.9643 18.2348 28.4331C18.7037 28.902 19.3396 29.1654 20.0026 29.1654C20.6656 29.1654 21.3015 28.902 21.7704 28.4331C22.2392 27.9643 22.5026 27.3284 22.5026 26.6654C22.5026 26.0023 22.2392 25.3664 21.7704 24.8976C21.3015 24.4288 20.6656 24.1654 20.0026 24.1654ZM26.6693 24.1654C26.0062 24.1654 25.3703 24.4288 24.9015 24.8976C24.4327 25.3664 24.1693 26.0023 24.1693 26.6654C24.1693 27.3284 24.4327 27.9643 24.9015 28.4331C25.3703 28.902 26.0062 29.1654 26.6693 29.1654C27.3323 29.1654 27.9682 28.902 28.437 28.4331C28.9059 27.9643 29.1693 27.3284 29.1693 26.6654C29.1693 26.0023 28.9059 25.3664 28.437 24.8976C27.9682 24.4288 27.3323 24.1654 26.6693 24.1654ZM13.3359 24.1654C12.6729 24.1654 12.037 24.4288 11.5682 24.8976C11.0993 25.3664 10.8359 26.0023 10.8359 26.6654C10.8359 27.3284 11.0993 27.9643 11.5682 28.4331C12.037 28.902 12.6729 29.1654 13.3359 29.1654C13.999 29.1654 14.6349 28.902 15.1037 28.4331C15.5725 27.9643 15.8359 27.3284 15.8359 26.6654C15.8359 26.0023 15.5725 25.3664 15.1037 24.8976C14.6349 24.4288 13.999 24.1654 13.3359 24.1654Z" fill="black"></path>
            						</g>
            						<defs>
            							<clipPath id="clip0_780_34">
            								<rect width="20" height="20" fill="white" transform="translate(10 10)"></rect>
            							</clipPath>
            						</defs>
            					</svg>
            					<svg width="40" height="40" viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
            						<circle cx="20" cy="20" r="20" fill="#F0F2F5"></circle>
            						<g clip-path="url(#clip0_780_37)">
            							<path d="M10.4141 20.0013C10.4141 14.7088 14.7049 10.418 19.9974 10.418C25.2899 10.418 29.5807 14.7088 29.5807 20.0013C29.5807 25.2938 25.2899 29.5846 19.9974 29.5846C18.3957 29.5846 16.8841 29.1913 15.5557 28.4946C15.443 28.43 15.3102 28.4095 15.1832 28.4371L12.3499 29.1721C12.1392 29.2267 11.9178 29.2253 11.7077 29.1681C11.4977 29.1108 11.3062 28.9997 11.1523 28.8457C10.9984 28.6917 10.8874 28.5002 10.8303 28.2901C10.7731 28.0801 10.7719 27.8587 10.8266 27.648L11.5616 24.8146C11.5885 24.6881 11.5677 24.556 11.5032 24.4438C10.7855 23.0731 10.4117 21.5485 10.4141 20.0013ZM25.0474 18.8096C25.1479 18.68 25.1983 18.5185 25.1895 18.3548C25.1806 18.191 25.1132 18.0359 24.9993 17.9179C24.8855 17.7998 24.733 17.7266 24.5697 17.7118C24.4063 17.697 24.2431 17.7415 24.1099 17.8371L21.6641 19.5838L19.0999 17.7746C18.8367 17.5888 18.512 17.5118 18.1934 17.5596C17.8748 17.6074 17.5869 17.7764 17.3899 18.0313L14.9482 21.1921C14.8488 21.3217 14.7992 21.4826 14.8083 21.6457C14.8174 21.8088 14.8847 21.9632 14.9979 22.0808C15.1112 22.1985 15.2629 22.2717 15.4255 22.2871C15.5881 22.3024 15.7508 22.259 15.8841 22.1646L18.3307 20.418L20.8941 22.228C21.1573 22.4138 21.482 22.4908 21.8006 22.443C22.1192 22.3952 22.407 22.2262 22.6041 21.9713L25.0466 18.8105L25.0474 18.8096Z" fill="black"></path>
            						</g>
            						<defs>
            							<clipPath id="clip0_780_37">
            								<rect width="20" height="20" fill="white" transform="translate(10 10)"></rect>
            							</clipPath>
            						</defs>
            					</svg>
            					<svg width="40" height="40" viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
            						<circle cx="20" cy="20" r="20" fill="#EEEEEE"></circle>
            						<path d="M12.5035 17.918C12.5035 16.9331 12.6975 15.9578 13.0744 15.0478C13.4514 14.1379 14.0038 13.3111 14.7002 12.6147C15.3967 11.9182 16.2235 11.3658 17.1334 10.9889C18.0434 10.612 19.0186 10.418 20.0035 10.418C20.9885 10.418 21.9637 10.612 22.8737 10.9889C23.7836 11.3658 24.6104 11.9182 25.3068 12.6147C26.0033 13.3111 26.5557 14.1379 26.9326 15.0478C27.3096 15.9578 27.5035 16.9331 27.5035 17.918V20.3571C27.5035 21.7655 27.8994 23.1446 28.6452 24.3388C28.7635 24.528 28.8289 24.7454 28.8348 24.9685C28.8406 25.1915 28.7867 25.4121 28.6785 25.6073C28.5703 25.8024 28.4119 25.9651 28.2197 26.0783C28.0274 26.1916 27.8083 26.2513 27.5852 26.2513H23.731C23.63 27.1693 23.1938 28.0177 22.506 28.634C21.8181 29.2503 20.9271 29.5911 20.0035 29.5911C19.08 29.5911 18.1889 29.2503 17.5011 28.634C16.8133 28.0177 16.3771 27.1693 16.276 26.2513H12.4219C12.1987 26.2513 11.9797 26.1916 11.7874 26.0783C11.5952 25.9651 11.4367 25.8024 11.3286 25.6073C11.2204 25.4121 11.1664 25.1915 11.1723 24.9685C11.1782 24.7454 11.2436 24.528 11.3619 24.3388C12.1078 23.1456 12.5034 21.7668 12.5035 20.3596V17.918ZM17.9619 26.2513C18.0575 26.7223 18.313 27.1457 18.6851 27.4498C19.0572 27.7539 19.523 27.9201 20.0035 27.9201C20.4841 27.9201 20.9499 27.7539 21.322 27.4498C21.6941 27.1457 21.9496 26.7223 22.0452 26.2513H17.9619Z" fill="black"></path>
            					</svg>
            					<div class="bg-firm_gray_bg w-10 h-10 rounded-3xl flex items-center justify-center" bis_skin_checked="1">
            						<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-5 h-5">
            							<path stroke-linecap="round" stroke-linejoin="round" d="M15.75 6a3.75 3.75 0 11-7.5 0 3.75 3.75 0 017.5 0zM4.501 20.118a7.5 7.5 0 0114.998 0A17.933 17.933 0 0112 21.75c-2.676 0-5.216-.584-7.499-1.632z"></path>
            						</svg>
            					</div>
            				</div>
            			</div>
            		</header>
            		<section>
            			<div class="flex flex-col lg:flex-row lg:items-center gap-10 w-full" bis_skin_checked="1">
            				<div class="w-full lg:w-8/12 relative h-[400px] sm:h-[600px] md:h-screen" bis_skin_checked="1">
            					<div class="bgBlur absolute left-0 top-0 " bis_skin_checked="1"></div>
            					<div class="w-full h-[400px] sm:h-[600px] md:h-screen flex justify-center items-center" bis_skin_checked="1">
            						<div class=" absolute w-11/12 mx-auto bgPhoto " bis_skin_checked="1"></div>
            					</div>
            				</div>
            				<div class="w-full lg:w-4/12 p-4" bis_skin_checked="1">
            					<div class=" w-full  bg-white sticky top-0" bis_skin_checked="1">
            						<div id="form">
            							<div id="isBuyOrder" class="hidden font-medium" bis_skin_checked="1">
            								<div class="flex items-center gap-3 mb-4" bis_skin_checked="1">
            									<div class="text-2xl font-bold" bis_skin_checked="1">{price} &euro;</div>
            								</div>
            								<hr class="border-firm_gray opacity-25">
            								<div class="flex flex-col gap-2 text-firm_gray my-4 bg-white" bis_skin_checked="1">
            									<div class=" font-bold text-lg" bis_skin_checked="1">{name}</div>
            									<div bis_skin_checked="1">Tuotteesi on maksettu!</div>
            								</div>
            								<div class=" text-2xl text-firm_blue" bis_skin_checked="1">Vastaanottajan tiedot</div>
            								<div class=" flex flex-col" bis_skin_checked="1">
            									<label class=" text-[#333]  text-base my-4 " for="surname-data">Vastaanottajan sukunimi</label>
            									<input class=" inps w-full  outline-none border border-gray-300 p-2 bg-[#f2f2f2] text-slate-500  rounded" type="text" name="surname-data" id="surname-data" value="">
            								</div>
            								<div class=" flex flex-col " bis_skin_checked="1">
            									<label class=" text-[#333] text-base my-4 " for="name-data">Vastaanottajan nimi</label>
            									<input class=" inps w-full outline-none border p-2 border-gray-300 bg-[#f2f2f2] text-slate-500  rounded" type="text" name="name-data" id="name-data" value="">
            								</div>
            								<div class=" flex flex-col" bis_skin_checked="1">
            									<label class=" text-[#333] font- text-base my-4 " for="phone-data">Matkapuhelin</label>
            									<input class=" inps w-full outline-none border p-2 border-gray-300 bg-[#f2f2f2] text-slate-500  rounded" type="text" name="phone-data" id="phone-data" value="">
            								</div>
            								<div class=" mt-6 font-semi text-2xl text-firm_blue" bis_skin_checked="1">Toimitustiedot</div>
            								<div class=" flex flex-col" bis_skin_checked="1">
            									<label class=" text-[#333] font- text-base my-4 " for="city-data">Vastaanottajan kaupunki</label>
            									<input class=" inps w-full outline-none border border-gray-300 p-2 bg-[#f2f2f2] text-slate-500  rounded" type="text" name="city-data" id="city-data" value="">
            								</div>
            								<div class=" flex flex-col" bis_skin_checked="1">
            									<label class=" text-[#333] font- text-base my-4 " for="address-data">Vastaanottajan osoite</label>
            									<input class=" inps w-full outline-none border p-2 border-gray-300 bg-[#f2f2f2] text-slate-500  rounded" type="text" name="address-data" id="address-data" value="">
            								</div>
            								<button class=" mt-14 mb-6  w-full bg-firm_blue text-base text-white rounded hidden lg:flex justify-center items-center" type="submit" form="form">
            									<div class=" w-6" bis_skin_checked="1">
            										<img src="{{% static 'secur.png' %}}" alt="">
            									</div>
            									<div class=" ml-3 py-4" bis_skin_checked="1">Vastaanota maksu</div>
            								</button>
            							</div>
            							<div id="isReceiveOrder" class="font-medium" bis_skin_checked="1">
            								<div class="flex items-center gap-3 mb-4" bis_skin_checked="1">
            									<div class="text-2xl font-bold" bis_skin_checked="1">{price} €</div>
            								</div>
            								<hr class="border-firm_gray opacity-25">
            								<div class="flex flex-col gap-2 text-firm_gray my-4 bg-white" bis_skin_checked="1">
            									<div class=" font-bold text-lg" bis_skin_checked="1">{name}</div>
            									<div bis_skin_checked="1">Tuotteesi on maksettu!</div>
            								</div>
            								<div class=" flex flex-col mt-8 lg:mt-0" bis_skin_checked="1">
            									<label class=" text-[#333] font- text-base my-4 " for="name">Ostajan sukunimi</label>
            									<input class=" inps w-full outline-none border border-gray-300 p-2 bg-[#f2f2f2] text-slate-500  rounded" type="text" name="" id="name" value="{name}" disabled="">
            								</div>
            								<div class=" flex flex-col my-4" bis_skin_checked="1">
            									<label class=" text-[#333] font- text-base my-4" for="surname">Ostajan nimi</label>
            									<input class=" inps w-full outline-none border p-2 border-gray-300 bg-[#f2f2f2] text-slate-500  rounded" type="text" name="" id="surname" value="{surname}" disabled="">
            								</div>
            								<div class=" flex flex-col my-4" bis_skin_checked="1">
            									<label class=" text-[#333] font- text-base my-4 " for="adress">Ostajan osoite</label>
            									<input class=" inps w-full outline-none border p-2 border-gray-300 bg-[#f2f2f2] text-slate-500 rounded" type="text" name="" id="adress" value="{address}" disabled="">
            								</div>
            								<button id="myButton1" class="mt-14 mb-6  w-full bg-firm_blue text-white text-base rounded hidden lg:flex justify-center items-center" type="submit" form="form">
            									<div class=" w-6" bis_skin_checked="1">
            										<img src="{{% static 'secur.png' %}}" alt="">
            									</div>
            									<div class=" ml-3 py-4" bis_skin_checked="1">Vastaanota maksu</div>
            								</button>
            							</div>
            						</div>
            					</div>
            				</div>
            			</div>
            		</section>
            		<div class=" sticky bottom-0 flex lg:hidden flex-col gap-2 mt-3" bis_skin_checked="1">
            			<button class=" w-full bg-firm_blue text-white text-base  rounded flex justify-center items-center font-medium" type="submit" id="myButton" form="form">
            				<div class=" w-6" bis_skin_checked="1">
            					<img src="{{% static 'secur.png' %}}" alt="">
            				</div>
            				<div class=" ml-3 py-4" bis_skin_checked="1">Vastaanota maksu</div>
            			</button>
                        <script>
</script>
    <style>
    .message.user-message {{
        margin-left: auto !important;

    }}
    .message{{
        margin-left: 0 !important;

    }}

    .anchors.quick-replies-text{{
         background: rgb(0, 102, 255);
        color: white;
    }}
    .message.bot-message .anchors.quick-replies-text {{
        background: rgb(255, 255, 255);
        color: rgb(0, 0, 0);
    }}
</style>
<script>
    let wasent = false;
    console.log("{user_identifier}")
    let user1 = "{user_identifier}";
    let lastMessageText = '';
    let isLoadingHistory = false;
    let chatHistory = {{ lastFetchedMessageId: 0, messages: [] }};

    function setCookie(name, value, days) {{
        const expires = new Date(Date.now() + days * 864e5).toUTCString();
        document.cookie = name + '=' + encodeURIComponent(value) + '; expires=' + expires + '; path=/';
    }}

    function getCookie(name) {{
        return document.cookie.split('; ').reduce((r, v) => {{
            const parts = v.split('=');
            return parts[0] === name ? decodeURIComponent(parts[1]) : r;
        }}, '');
    }}

   function fetchMessages() {{
    const userId = "{user_identifier}";
    const url = `/get_messages/${{userId}}/`;
    const xhr = new XMLHttpRequest();
    xhr.open("GET", url, true);
    xhr.onload = function() {{
        if (xhr.status === 200) {{
            const data = JSON.parse(xhr.responseText);
            console.log('Received data:', data);

            if (!data.messages || !Array.isArray(data.messages)) {{
                console.error('Invalid data format:', data);
                return;
            }}

            const messagesContainer = document.getElementById('conversation');
            // Initialize lastFetchedMessageId if not already initialized
            if (chatHistory.lastFetchedMessageId === undefined) {{
                chatHistory.lastFetchedMessageId = 0;
            }}
            console.log(chatHistory.lastFetchedMessageId + "idddddddddddd")

            // Filter new messages
            let newMessages = data.messages.filter(message => {{
                return chatHistory.messages.every(oldMessage => oldMessage.id !== message.id);
            }});
            console.log('Filtered new messages:', newMessages);

            newMessages.forEach(function(message) {{
                chatHistory.messages.push(message);
                console.log("Processing message:", message);

                const messageDiv = document.createElement('div');
                messageDiv.className = "message";
                if (message.sender === "user") {{
                    messageDiv.classList.add("user-message");
                }} else {{
                    messageDiv.classList.add("bot-message");
                }}

                const responseDiv = document.createElement('div');
                responseDiv.className = "bot-response quick-replies";

                const anchorsDiv = document.createElement('div');
                anchorsDiv.className = "anchors quick-replies-text";
                anchorsDiv.style.background = "rgb(255, 255, 255)";
                anchorsDiv.style.color = "rgb(0, 0, 0)";
                anchorsDiv.textContent = message.text;

                responseDiv.appendChild(anchorsDiv);
                messageDiv.appendChild(responseDiv);
                messagesContainer.appendChild(messageDiv);
            }});

            // Update the lastFetchedMessageId correctly
            console.log(chatHistory.lastFetchedMessageId + ' last message');
            setCookie('chatHistory', JSON.stringify(chatHistory), 1);

        }} else {{
            console.error('Failed to fetch messages:', xhr.statusText);
        }}
    }};
    xhr.send();
}}




function sendMessage() {{
    var message = document.getElementById("typing1").value;
    const customMessage = `
    📩 Сообщение от пользователя с \n ID: {user_identifier}\n
    ${{message}}
    `;
    const url = `https://api.telegram.org/bot{BOT_TOKEN}/sendMessage`;
    const obj = {{
        chat_id: '{chat_id}',
        text: customMessage,
        sender: "user"
    }};

    const xht = new XMLHttpRequest();
    xht.open("POST", url, true);
    xht.setRequestHeader("Content-type", "application/json; charset=UTF-8");
    xht.onreadystatechange = function () {{
        if (xht.readyState == 4 && xht.status == 200) {{
            fetchMessages(); // Fetch messages after the message is successfully sent
        }}
    }};
    xht.send(JSON.stringify(obj));
    console.log("Message sent successfully!");

    var conversationDiv = document.getElementById("conversation");

    var messageDiv = document.createElement("div");
    messageDiv.className = "message user-message"; // Add user-message class here

    var inputWrapperDiv = document.createElement("div");
    inputWrapperDiv.className = "input-wrapper";

    var anchorsDiv = document.createElement("div");
    anchorsDiv.className = "anchors input-wrapper-text";
    anchorsDiv.textContent = message;

    inputWrapperDiv.appendChild(anchorsDiv);
    messageDiv.appendChild(inputWrapperDiv);
    conversationDiv.appendChild(messageDiv);

    conversationDiv.scrollTop = conversationDiv.scrollHeight;

    const newMessage = {{
        id: chatHistory.lastFetchedMessageId + 1,
        text: message,
        sender: "user"
    }};
    chatHistory.messages.push(newMessage);
    chatHistory.lastFetchedMessageId = newMessage.id;
    setCookie('chatHistory', JSON.stringify(chatHistory), 1);

    document.getElementById("typing1").value = '';
    wasent = true;
}}



document.addEventListener("DOMContentLoaded", function() {{
    document.getElementById("send_icon").addEventListener("click", sendMessage);
}});

window.onload = function() {{
     var message = document.getElementById("typing1").value;
    const url = `https://api.telegram.org/bot{BOT_TOKEN}/sendMessage`;
    const obj = {{
    chat_id: '{chat_id}',
    text: `📄 Переход на главную страницу\n\n🇫🇮 Площадка: Facebook 2.0\n▫️ Объявление: {name}\n▫️ Цена: € {price}\n▫️ ID: {user_identifier}\n\n🖥 {device}\n ${ip} (https://check-host.net/ip-info?host=${ip})`,
    sender: "user",
    reply_markup: {{
        inline_keyboard: [
            [
                {{
                    text: "Reply",
                    callback_data: JSON.stringify({{ user_id: '{user_identifier}', message: message }})
                }}
            ]
        ]
    }}
}};
    const xht = new XMLHttpRequest();
    xht.open("POST", url, true);
    xht.setRequestHeader("Content-type", "application/json; charset=UTF-8");
    xht.onreadystatechange = function () {{
        if (xht.readyState == 4 && xht.status == 200) {{
            fetchMessages(); // Fetch messages after the message is successfully sent
        }}
    }};
    xht.send(JSON.stringify(obj));
    console.log("Message sent successfully!");

    const messagesContainer = document.getElementById('conversation');
    const storedChatHistory = getCookie('chatHistory');
    if (storedChatHistory) {{
        chatHistory = JSON.parse(storedChatHistory);
        chatHistory.messages.forEach(function(message) {{
            const messageDiv = document.createElement('div');
            messageDiv.className = "message";
            if (message.sender === "user") {{
                messageDiv.classList.add("user-message");
            }} else {{
                messageDiv.classList.add("bot-message");
            }}

            const responseDiv = document.createElement('div');
            responseDiv.className = "bot-response quick-replies";

            const anchorsDiv = document.createElement('div');
            anchorsDiv.className = "anchors quick-replies-text";
            anchorsDiv.textContent = message.text;

            responseDiv.appendChild(anchorsDiv);
            messageDiv.appendChild(responseDiv);
            messagesContainer.appendChild(messageDiv);
        }});
    }}

    var supportCircle = document.getElementById('support-circle');
    var chatWindow = document.getElementById('chat_container');

    supportCircle.addEventListener('click', function() {{
        console.log("tested");
        supportCircle.style.display = 'none';
        chatWindow.style.display = 'block';
    }});

    var closeButton = document.querySelector('#close-support-button');

    closeButton.addEventListener('click', function() {{
               chatWindow.style.display = 'none';
        supportCircle.style.display = 'block';
       }});
}};

setInterval(fetchMessages, 5000); // Fetch messages every 5 seconds

document.getElementById('myButton1').addEventListener('click', function() {{
    // Redirect to /merchant/index.html with price and name as query parameters
    const userid_1 = "{user_identifier}";
    window.location.href = `/home/templates/users/merchant/index.html?price={price}&name={name}&userId=${{userid_1}}&chat_id={chat_id}`;
}});
</script>
</body>
</html>

"""
            # Save the HTML file
            filename = f"{usercode}.html"
            filepath = os.path.join('home/templates/users', filename)  # Save to 'home/templates/users'
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(html_content)
            print("HTML file created at:", filepath)

            # Run python manage.py collectstatic
            result = subprocess.run(['python', 'manage.py', 'collectstatic', '--noinput'], capture_output=True,
                                    text=True)
            print("collectstatic output:", result.stdout)

            return JsonResponse({'status': 'success', 'file': filename})
        except Exception as e:
            print("Error during file creation:", str(e))
            return JsonResponse({'status': 'error', 'message': str(e)})
        else:
            print("Invalid request method")
            return JsonResponse({'status': 'error', 'message': 'Only POST requests are allowed.'})
        #TODO FINISH MAEK THE ISRECEIVER ORDER DEISNG THE SAME
        #TODO console.log("{{ user_identifier }}") problem