import requests
import random
from django.shortcuts import render, get_object_or_404
from pedidos.models import Pedido, ItemPedido

POKEMON_API_URL = "https://pokeapi.co/api/v2/pokemon/"

def obtener_pokemon_aleatorio():
    """Obtiene un Pokémon aleatorio de la API."""
    try:
        pokemon_id = random.randint(1, 151)  # Solo los primeros 151 Pokémon
        response = requests.get(f"{POKEMON_API_URL}{pokemon_id}/", timeout=5)
        response.raise_for_status()
        data = response.json()
        return {"id": pokemon_id, "name": data["name"].capitalize()}
    except requests.exceptions.RequestException as e:
        print(f"Error al obtener Pokémon: {e}")
        return None

def detalle_pedido(request, pedido_numero):
    """Muestra los detalles del pedido y asigna un Pokémon a la Cajita Feliz si no tiene uno."""
    pedido = get_object_or_404(Pedido, numero=pedido_numero)
    items_cajita = pedido.items.filter(producto__nombre="Cajita Feliz")

    for item in items_cajita:
        if not item.pokemon_id:  # 🔹 Solo asigna un Pokémon si aún no tiene uno
            pokemon = obtener_pokemon_aleatorio()
            if pokemon:
                item.pokemon_id = pokemon["id"]
                item.pokemon_nombre = pokemon["name"]
                item.save()

    return render(request, 'cliente/detalle_pedido.html', {'pedido': pedido, 'items_cajita': items_cajita})

def ver_pokemon_pedido(request, pedido_numero):
    """Muestra el Pokémon asignado al pedido."""
    pedido = get_object_or_404(Pedido, numero=pedido_numero)
    items_cajita = pedido.items.filter(producto__nombre="Cajita Feliz")

    return render(request, "pedido_pokemon.html", {
        "pedido": pedido,
        "items_cajita": items_cajita
    })
