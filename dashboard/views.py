from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings
from django.contrib.auth.decorators import login_required

import requests
from datetime import datetime, timezone
from collections import defaultdict
import json


@login_required
def index(request):
    response = requests.get(settings.API_URL)
    posts = response.json()

    users_msg = get_users_msg(posts)
    avg_msg_length = get_avg_msg_length(posts)
    total_responses = len(posts)
    user_stats = get_user_stats(posts)
    chart_config = chart_data(posts)

    data = {
        'title': "Landing Page\' Dashboard",
        'total_responses': total_responses,
        'avg_msg_length': avg_msg_length,
        'comments': users_msg,
        'most_active_user': user_stats['usuario_mas_activo'],
        'oldest_user': user_stats['oldest_user'],
        'chart_data': json.dumps(chart_config),
    }
    
    return render(request, 'dashboard/index.html', data)

def get_users_msg(response):
    return [{'name': element['name'], 'message': element['message']} for element in response.values()]

def get_avg_msg_length(response):
    total_length = sum([len(element['message']) for element in response.values()])
    total_responses = len(response)
    return round(total_length / total_responses, 1) if total_responses > 0 else 0

def chart_data(response):
    responses_by_date = defaultdict(int)
    
    for post_id, post_data in response.items():
        current_date = None
        if 'date' in post_data:
            try:
                current_date = datetime.fromisoformat(post_data['date'].replace('Z', '+00:00'))
            except (ValueError, TypeError):
                pass

        if current_date:
            date_key = current_date.strftime('%Y-%m-%d')
            responses_by_date[date_key] += 1
    
    sorted_dates = sorted(responses_by_date.keys())
    labels = []
    data_points = []
    cumulative_count = 0
    
    for date_str in sorted_dates:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        formatted_date = date_obj.strftime('%d/%m/%Y')
        labels.append(formatted_date)

        cumulative_count += responses_by_date[date_str]
        data_points.append(cumulative_count)

    chart_config = {
        'labels': labels,
        'datasets': [
            {
                'label': 'Respuestas Acumuladas',
                'backgroundColor': '#0694a2',
                'borderColor': '#0694a2',
                'data': data_points,
                'fill': False,
            },
            {
                'label': 'Respuestas Diarias',
                'backgroundColor': '#7e3af2',
                'borderColor': '#7e3af2',
                'data': [responses_by_date[date] for date in sorted_dates],
                'fill': False,
            }
        ]
    }

    return chart_config

def get_user_stats(response):
    conteo_usuarios = {}
    oldest_user = None
    earliest_date = datetime.max.replace(tzinfo=timezone.utc)

    for post_id, post_data in response.items():
        nombre_autor = post_data['name']
        conteo_usuarios[nombre_autor] = conteo_usuarios.get(nombre_autor, 0) + 1

        current_date = None
    
        if 'date' in post_data:
            try:
                current_date = datetime.fromisoformat(post_data['date'].replace('Z', '+00:00'))
            except (ValueError, TypeError):
                pass

        if current_date and current_date < earliest_date:
            earliest_date = current_date
            oldest_user = post_data['name']

    usuario_mas_activo = max(conteo_usuarios, key=conteo_usuarios.get) if conteo_usuarios else None

    return {
        'conteo_usuarios': conteo_usuarios,
        'usuario_mas_activo': usuario_mas_activo,
        'oldest_user': oldest_user
    }