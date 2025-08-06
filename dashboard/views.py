from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse

import requests
from django.conf import settings

def get_avg_msg_length(response):
    total_length = sum([len(element['message']) for element in response.json().values()])
    total_responses = len(response.json())
    return round(total_length / total_responses, 1) if total_responses > 0 else 0

def index(request):
    response = requests.get(settings.API_URL)
    posts = response.json()
    total_responses = len(posts)

    data = {
        'title': "Landing Page' Dashboard",
        'total_responses': total_responses,
        'avg_msg_length': get_avg_msg_length(response),
        'posts': posts.values(),
    }
    
    return render(request, 'dashboard/index.html', data)