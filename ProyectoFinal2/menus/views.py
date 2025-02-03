from django.shortcuts import render
from menus.models import Producto

def ver_menu(request):
    """Muestra el menú con detalles adicionales."""
    productos = Producto.objects.select_related('categoria').all()
    return render(request, 'menu/ver_menu.html', {'productos': productos})
