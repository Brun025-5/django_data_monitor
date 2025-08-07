from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings
from django.contrib.auth.decorators import login_required

import requests
from datetime import datetime, timezone

def get_avg_msg_length(response):
    total_length = sum([len(element['message']) for element in response.json().values()])
    total_responses = len(response.json())
    return round(total_length / total_responses, 1) if total_responses > 0 else 0

@login_required
def index(request):
    response = requests.get(settings.API_URL)
    posts = response.json()
    total_responses = len(posts)

    conteo_usuarios = {}

    oldest_user = None
    earliest_date = datetime.max.replace(tzinfo=timezone.utc)

    for post_id, post_data in posts.items():
        nombre_autor = post_data['name']
        conteo_usuarios[nombre_autor] = conteo_usuarios.get(nombre_autor, 0) + 1

        current_date = None
    
        # Intentamos leer la fecha en formato ISO 8601 (el más común en tu JSON)
        if 'date' in post_data:
            try:
                # Reemplazamos 'Z' por '+00:00' para que Python lo entienda como UTC
                current_date = datetime.fromisoformat(post_data['date'].replace('Z', '+00:00'))
            except (ValueError, TypeError):
                # Si falla, current_date seguirá siendo None y se intentará el siguiente formato
                pass
                
        # Si el formato anterior no funcionó o no existía, intentamos con el campo 'timestamp'
        if not current_date and 'timestamp' in post_data:
            try:
                # Primero, lo parseamos como una fecha sin zona horaria (naive)
                naive_date = datetime.strptime(post_data['timestamp'], '%d/%m/%Y, %I:%M:%S %p')
                # Luego, asumimos que está en UTC y la convertimos a timezone-aware
                current_date = naive_date.replace(tzinfo=timezone.utc)
            except (ValueError, TypeError):
                # Si el formato es desconocido, simplemente lo ignoramos
                pass

        # Si logramos obtener una fecha, la comparamos
        if current_date and current_date < earliest_date:
            earliest_date = current_date
            oldest_user = post_data['name']


    # Encontrar al usuario con más mensajes
    usuario_mas_activo = max(conteo_usuarios, key=conteo_usuarios.get)
    mensajes_usuario_mas_activo = conteo_usuarios[usuario_mas_activo]

    data = {
        'title': "Landing Page' Dashboard",
        'total_responses': total_responses,
        'avg_msg_length': get_avg_msg_length(response),
        'posts': posts.values(),
        'most_active_user': usuario_mas_activo,
        'oldest_user': oldest_user,
    }
    
    return render(request, 'dashboard/index.html', data)