from django.shortcuts import render
from inventario.models import Insumo  # Asegúrate de importar el modelo correcto

def vista_inventario(request):
    """Muestra el estado del inventario con la cantidad real de los insumos."""
    insumos = Insumo.objects.all()  # Asegurar que se obtienen todos los insumos correctamente
    return render(request, 'inventario/ver_inventario.html', {'insumos': insumos})
