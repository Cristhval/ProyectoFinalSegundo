import requests
import random
from django.shortcuts import render

POKEMON_API_URL = "https://pokeapi.co/api/v2/pokemon/"

def obtener_pokemon_aleatorio():
    pokemon_id = random.randint(1, 151)  # Solo los primeros 151
    response = requests.get(f"{POKEMON_API_URL}{pokemon_id}/")
    return response.json() if response.status_code == 200 else None

def pedido_con_pokemon(request):
    pokemon = obtener_pokemon_aleatorio()
    return render(request, "pedido_pokemon.html", {"pokemon": pokemon})
