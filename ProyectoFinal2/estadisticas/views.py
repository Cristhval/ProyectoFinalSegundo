from django.http import HttpResponse
from django.shortcuts import render
from django.db.models import Count, Sum
from datetime import datetime
import matplotlib.pyplot as plt
import io
import base64

from django.template.loader import render_to_string

from .models import Estadistica, Reporte
from facturacion.models import ItemFactura


def dashboard_estadisticas(request):
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')

    # Obtén la última estadística registrada
    estadistica = Estadistica.objects.order_by('-fecha_inicio').first()

    if not estadistica:
        return render(request, "estadisticas/dashboard.html", {
            "mejor_mesero": "No disponible",
            "mesa_mas_usada": "No disponible",
            "producto_mas_vendido": "No disponible",
            "grafico_ventas": None,
        })

    # 🔹 Asegurar que los datos de ventas son correctos
    ventas = (
        ItemFactura.objects
        .filter(factura__fecha__range=[estadistica.fecha_inicio, estadistica.fecha_fin])
        .values("item_pedido__producto__nombre")
        .annotate(total_vendido=Sum("cantidad"))
        .order_by("-total_vendido")
    )

    productos = [venta["item_pedido__producto__nombre"] for venta in ventas]
    cantidades = [venta["total_vendido"] for venta in ventas]

    # 🔹 Generar el gráfico solo si hay datos
    img_str = None
    if productos and cantidades:
        plt.figure(figsize=(6, 4))
        plt.bar(productos, cantidades, color="blue")
        plt.xlabel("Producto")
        plt.ylabel("Cantidad Vendida")
        plt.title("Ventas por Producto")
        plt.xticks(rotation=45, ha="right")

        buffer = io.BytesIO()
        plt.savefig(buffer, format="png")
        buffer.seek(0)
        img_str = base64.b64encode(buffer.read()).decode("utf-8")
        plt.close()

    context = {
        "mejor_mesero": estadistica.mejor_mesero or "No disponible",
        "mesa_mas_usada": estadistica.mesa_mas_usada or "No disponible",
        "producto_mas_vendido": estadistica.producto_mas_vendido or "No disponible",
        "grafico_ventas": img_str,
    }

    return render(request, "estadisticas/dashboard.html", context)


def generar_reporte_pdf(request, reporte_id):
    reporte = Reporte.objects.get(id=reporte_id)
    return exportar_estadisticas_pdf(request, reporte.fecha_inicio, reporte.fecha_fin)


def exportar_estadisticas_pdf(request, fecha_inicio, fecha_fin):
    """Genera un PDF con las estadísticas de un rango de fechas."""
    estadistica = Estadistica.objects.filter(fecha_inicio=fecha_inicio, fecha_fin=fecha_fin).first()

    if not estadistica:
        return HttpResponse("No hay estadísticas disponibles para este rango de fechas.", content_type="text/plain")

    context = {
        "titulo": estadistica.titulo,
        "mejor_mesero": estadistica.mejor_mesero,
        "mesa_mas_usada": estadistica.mesa_mas_usada,
        "producto_mas_vendido": estadistica.producto_mas_vendido,
        "fecha_inicio": estadistica.fecha_inicio,
        "fecha_fin": estadistica.fecha_fin,
    }

    html = render_to_string("estadisticas/estadisticas_pdf.html", context)

    try:
        import pdfkit
        pdf = pdfkit.from_string(html, False)
        response = HttpResponse(pdf, content_type="application/pdf")
        response["Content-Disposition"] = f'attachment; filename="Estadisticas_{fecha_inicio}_a_{fecha_fin}.pdf"'
        return response
    except ImportError:
        return HttpResponse("Error al generar el PDF. Instala pdfkit.", content_type="text/plain")

def generar_reporte_pdf(request, reporte_id):
    reporte = Reporte.objects.get(id=reporte_id)
    return exportar_estadisticas_pdf(request, reporte.fecha_inicio, reporte.fecha_fin)

def exportar_estadisticas_pdf(request, fecha_inicio, fecha_fin, pdfkit=None):
    """Genera un PDF con las estadísticas de un rango de fechas."""
    estadistica = Estadistica.objects.filter(fecha_inicio=fecha_inicio, fecha_fin=fecha_fin).first()

    if not estadistica:
        return HttpResponse("No hay estadísticas disponibles para este rango de fechas.", content_type="text/plain")

    context = {
        "titulo": estadistica.titulo,
        "mejor_mesero": estadistica.mejor_mesero,
        "mesa_mas_usada": estadistica.mesa_mas_usada,
        "producto_mas_vendido": estadistica.producto_mas_vendido,
        "fecha_inicio": estadistica.fecha_inicio,
        "fecha_fin": estadistica.fecha_fin,
    }

    html = render_to_string("estadisticas/estadisticas_pdf.html", context)
    pdf = pdfkit.from_string(html, False)

    response = HttpResponse(pdf, content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="Estadisticas_{fecha_inicio}_a_{fecha_fin}.pdf"'
    return response