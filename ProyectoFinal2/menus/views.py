from django.shortcuts import render
from menus.models import Producto, Categoria


def ver_menu(request):
    """Muestra el menú con detalles adicionales y categorías para el filtro."""
    productos = Producto.objects.select_related('categoria').all()
    categorias = Categoria.objects.all()  # Obtener todas las categorías
    return render(request, 'menu/ver_menu.html', {'productos': productos, 'categorias': categorias})