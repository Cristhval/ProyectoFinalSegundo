import requests
import random
from django.shortcuts import render, get_object_or_404
from pedidos.models import Pedido, ItemPedido, EstadoPedido
from mesas.models import Mesa
from django.contrib.auth.decorators import login_required
from menus.models import Producto
from django.shortcuts import redirect

from util.models import Cliente

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

@login_required
def crear_pedido(request, producto_id=None):
    """Permite crear un pedido desde la vista o directamente desde el menú."""

    # Verificar si el usuario autenticado es un empleado
    if not request.user.is_authenticated or (not request.user.es_mesero() and not request.user.es_admin()):
        return redirect('login')

    # Si el pedido se crea desde el menú con un producto específico
    if producto_id:
        cliente = request.user.cliente if hasattr(request.user, 'cliente') else None
        if not cliente:
            return redirect('vista_cliente')

        mesa_disponible = Mesa.objects.filter(estado="LIBRE").first()
        if not mesa_disponible:
            return render(request, 'pedidos/crear_pedido.html', {'error': "No hay mesas disponibles."})

        pedido = Pedido.objects.create(cliente=cliente, mesa=mesa_disponible, estado="EN_PROCESO")
        producto = get_object_or_404(Producto, id=producto_id)
        ItemPedido.objects.create(pedido=pedido, producto=producto, cantidad=1, cliente=cliente)

        return redirect('vista_empleado')

    if request.method == "POST":
        cliente_id = request.POST.get("cliente")
        mesa_id = request.POST.get("mesa")
        productos_ids = request.POST.getlist("productos")

        if not cliente_id:
            return render(request, 'pedidos/crear_pedido.html', {
                'error': "Debe seleccionar un cliente.",
                'mesas': Mesa.objects.filter(estado="LIBRE"),
                'productos': Producto.objects.filter(disponibilidad=True),
                'clientes': Cliente.objects.filter(activo=True)
            })

        cliente = get_object_or_404(Cliente, id=cliente_id)
        mesa = get_object_or_404(Mesa, id=mesa_id)

        pedido = Pedido.objects.create(cliente=cliente, mesa=mesa, estado="EN_PROCESO")

        for producto_id in productos_ids:
            producto = get_object_or_404(Producto, id=producto_id)
            cantidad = int(request.POST.get(f"cantidad_{producto_id}", 1))  # Obtiene la cantidad seleccionada
            ItemPedido.objects.create(pedido=pedido, producto=producto, cantidad=cantidad, cliente=cliente)

        return redirect('vista_empleado')

    # Obtener listas para el formulario de creación manual
    mesas = Mesa.objects.filter(estado="LIBRE")
    productos = Producto.objects.filter(disponibilidad=True)
    clientes = Cliente.objects.filter(activo=True)

    return render(request, 'pedidos/crear_pedido.html', {'mesas': mesas, 'productos': productos, 'clientes': clientes})

@login_required
def lista_pedidos(request):
    """Muestra la lista de pedidos y permite filtrarlos por estado."""
    filtro_estado = request.GET.get('estado', '')

    pedidos = Pedido.objects.all().order_by('-fecha_actual')  # Ordenar por fecha
    if filtro_estado:
        pedidos = pedidos.filter(estado=filtro_estado)

    return render(request, 'pedidos/pedidos.html', {'pedidos': pedidos, 'filtro_estado': filtro_estado})


@login_required
def editar_pedido(request, pedido_numero):
    pedido = get_object_or_404(Pedido, numero=pedido_numero)  # Buscar por `numero`
    productos_disponibles = Producto.objects.filter(disponibilidad=True)

    if request.method == "POST":
        # 🔹 Actualizar el estado del pedido
        estado = request.POST.get("estado")
        if not estado:
            return render(request, "pedidos/editar_pedido.html", {
                "pedido": pedido,
                "productos": productos_disponibles,
                "error": "El estado del pedido es obligatorio."
            })
        pedido.estado = estado

        # 🔹 Manejar eliminación de productos
        productos_a_eliminar = request.POST.getlist("eliminar_productos")
        if productos_a_eliminar:
            pedido.items.filter(producto_id__in=productos_a_eliminar).delete()

        # 🔹 Manejar productos existentes (actualizar cantidad)
        for item in pedido.items.all():
            cantidad = request.POST.get(f"cantidad_{item.producto.id}")
            if cantidad:
                item.cantidad = int(cantidad)
                item.save()

        # 🔹 Agregar nuevos productos seleccionados
        nuevos_productos_ids = request.POST.getlist("nuevos_productos")
        for producto_id in nuevos_productos_ids:
            cantidad_nueva = int(request.POST.get(f"cantidad_nuevo_{producto_id}", 1))
            producto = get_object_or_404(Producto, id=producto_id)
            ItemPedido.objects.create(pedido=pedido, producto=producto, cantidad=cantidad_nueva, cliente=pedido.cliente)

        pedido.save()  # Guardar cambios en el pedido
        return redirect("lista_pedidos")

    return render(request, "pedidos/editar_pedido.html", {
        "pedido": pedido,
        "productos": productos_disponibles,
        "EstadoPedido": EstadoPedido  # Para acceder a los estados en la plantilla
    })


@login_required
def ver_pedidos(request):
    pedidos = Pedido.objects.all().order_by('-fecha_actual')
    return render(request, 'pedidos/ver_pedidos.html', {'pedidos': pedidos})
