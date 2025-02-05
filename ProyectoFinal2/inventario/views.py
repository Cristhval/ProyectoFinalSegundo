from django.db.models import Sum
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils.dateparse import parse_date
from django.utils.timezone import now

from inventario.models import Insumo, Operacion, Alerta, Inventario, ReporteBodega, ReporteConsumo


def vista_inventario(request):
    """Muestra el estado del inventario con insumos, alertas y últimos movimientos."""
    insumos = Insumo.objects.all()
    alertas = Alerta.objects.all().order_by('-fecha')[:5]  # Últimas 5 alertas
    operaciones = Operacion.objects.all().order_by('-fechaRegistro')[:5]  # Últimos 5 movimientos

    return render(request, 'inventario/ver_inventario.html', {
        'insumos': insumos,
        'alertas': alertas,
        'operaciones': operaciones,
        'almacen': "Almacén"  # Nombre fijo del inventario
    })


def gestionar_inventario(request):
    """Permite agregar o retirar insumos del inventario con observaciones y filtrar movimientos por fechas."""
    insumos = Insumo.objects.all()
    operaciones = Operacion.objects.all().order_by('-fechaRegistro')  # Últimos movimientos

    # Filtrar por fechas si se envían
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')

    if fecha_inicio and fecha_fin:
        fecha_inicio = parse_date(fecha_inicio)
        fecha_fin = parse_date(fecha_fin)
        if fecha_inicio and fecha_fin:
            operaciones = operaciones.filter(fechaRegistro__date__gte=fecha_inicio, fechaRegistro__date__lte=fecha_fin)

    if request.method == 'POST':
        insumo_id = request.POST.get('insumo')
        cantidad = int(request.POST.get('cantidad'))
        tipo = request.POST.get('tipo')
        observaciones = request.POST.get('observaciones', '')

        insumo = Insumo.objects.get(id=insumo_id)

        # Validaciones
        if tipo == 'salida' and cantidad > insumo.cantidadDisponible:
            messages.error(request, "No puedes retirar más de lo disponible.")
        else:
            # Crear operación con observaciones
            Operacion.objects.create(
                insumo=insumo,
                cantidad=cantidad,
                tipo=tipo,
                observaciones=observaciones
            )

            messages.success(request, f"Operación de {tipo} realizada correctamente.")

        return redirect('gestionar_inventario')

    return render(request, 'inventario/gestionar_invetario.html', {
        'insumos': insumos,
        'operaciones': operaciones,
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin
    })


def generar_reporte_consumo(request):
    """Genera un reporte de consumo de insumos solo cuando se retira un producto."""
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')

    reportes = []
    total_retirado = 0

    if fecha_inicio and fecha_fin:
        fecha_inicio = parse_date(fecha_inicio)
        fecha_fin = parse_date(fecha_fin)

        if fecha_inicio and fecha_fin:
            reportes = Operacion.objects.filter(
                tipo='salida',
                fechaRegistro__date__gte=fecha_inicio,
                fechaRegistro__date__lte=fecha_fin
            ).values('insumo__nombre').annotate(total=Sum('cantidad')).order_by('insumo__nombre')

            # Calcular el total de todos los insumos retirados
            total_retirado = sum(item['total'] for item in reportes)

    return render(request, 'inventario/reporte_consumo.html', {
        'reportes': reportes,
        'total_retirado': total_retirado
    })

def generar_reporte_bodega(request):
    """Genera un reporte diario del estado del inventario, permitiendo filtrar por fecha."""
    fecha_str = request.GET.get('fecha')  # Obtener la fecha desde el formulario

    if fecha_str:
        fecha = parse_date(fecha_str)  # Convertir la fecha a objeto datetime.date
    else:
        fecha = now().date()  # Si no se elige fecha, usa la fecha de hoy

    # Obtener el total de insumos disponibles actualmente
    total_insumos = Insumo.objects.aggregate(total=Sum('cantidadDisponible'))['total'] or 0

    # Obtener el total de insumos ingresados en la fecha seleccionada
    total_ingresados_hoy = Operacion.objects.filter(
        tipo='entrada',
        fechaRegistro__date=fecha
    ).aggregate(total=Sum('cantidad'))['total'] or 0

    reporte = {
        "fecha": fecha,
        "total_insumos": total_insumos,
        "total_ingresados_hoy": total_ingresados_hoy
    }

    return render(request, 'inventario/reporte_bodega.html', {
        'reporte': reporte,
        'fecha': fecha_str  # Mantener la fecha en el input del formulario
    })