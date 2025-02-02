import requests
from django.db import transaction
from django.shortcuts import render, get_object_or_404, redirect

from pedidos.models import Pedido
from .models import Promocion, ItemFactura
from django.contrib import messages
from facturacion.models import Factura, PagoEfectivo, PagoTarjeta, PagoTransferencia
from util.models import Cliente
from django.contrib.auth.decorators import login_required
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from django.http import HttpResponse, FileResponse, JsonResponse
import io
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer
from reportlab.lib import colors
API_KEY = "961bd7eac250b1785c38e99bfe913eef"
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"


def obtener_clima(ciudad="Loja,EC"):
    """ Obtiene el clima actual de una ciudad a través de la API de OpenWeather """
    params = {"q": ciudad, "appid": API_KEY, "units": "metric", "lang": "es"}

    try:
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()  # Lanza error si la respuesta no es 200

        return response.json()

    except requests.exceptions.RequestException as e:
        print(f"Error al obtener el clima: {e}")  # Opcional: Registrar en logs
        return None  # Devolvemos None en caso de error


def promociones_por_clima(request):
    """ Filtra promociones según el clima actual """
    clima = obtener_clima("Loja,EC")
    promociones = []

    if clima:
        try:
            descripcion_clima = clima["weather"][0]["description"]
            print(f"🌦 Clima actual: {descripcion_clima}")  # Debugging (opcional)

            # Filtramos promociones que coincidan con la descripción del clima
            promociones = Promocion.objects.filter(tipo_clima__icontains=descripcion_clima, activa=True)

            if not promociones:
                messages.info(request, "No hay promociones activas para este clima.")

        except (KeyError, IndexError) as e:
            print(f"Error al procesar el clima: {e}")
            messages.error(request, "No se pudo obtener el clima correctamente.")

    else:
        messages.error(request, "No se pudo conectar con la API del clima.")

    return render(request, "facturacion/promociones.html", {"promociones": promociones, "clima": clima})



@login_required
def vista_metodos_pago(request, factura_numero):
    factura = get_object_or_404(Factura, numero=factura_numero)

    # Obtener pagos asociados a la factura
    pagos_efectivo = PagoEfectivo.objects.filter(factura=factura)
    pagos_tarjeta = PagoTarjeta.objects.filter(factura=factura)
    pagos_transferencia = PagoTransferencia.objects.filter(factura=factura)

    # Unificar los métodos de pago en una lista para la plantilla
    pagos = []
    for pago in pagos_efectivo:
        pagos.append({"metodo": "Efectivo", "monto": pago.monto_pagado})
    for pago in pagos_tarjeta:
        pagos.append({"metodo": "Tarjeta", "monto": pago.monto_pagado})
    for pago in pagos_transferencia:
        pagos.append({"metodo": "Transferencia", "monto": pago.monto_pagado})

    context = {
        'factura': factura,
        'pagos': pagos,
    }
    return render(request, 'facturacion/metodos_pago.html', context)

@login_required
def lista_facturas(request):
    """Muestra el historial de facturas del cliente autenticado."""
    cliente = request.user.cliente
    facturas = Factura.objects.filter(pedido__cliente=cliente).order_by('-fecha')
    return render(request, 'facturacion/factura_lista.html', {'facturas': facturas})

@login_required
def detalle_factura(request, factura_numero):
    """Muestra el detalle de una factura específica."""
    factura = get_object_or_404(Factura, numero=factura_numero)
    items = factura.items.all()  # ✅ Asegurar que los productos se envían a la plantilla

    return render(request, 'facturacion/factura_detalle.html', {
        'factura': factura,
        'items': items
    })


def descargar_factura_pdf(request, factura_numero):
    factura = get_object_or_404(Factura, numero=factura_numero)
    items = factura.items.all()

    buffer = io.BytesIO()
    pdf = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()

    # Encabezado de la factura
    elements.append(Paragraph("<b>FastFood Express</b>", styles['Title']))
    elements.append(Paragraph("Dirección: Av. Principal #123, Loja, Ecuador", styles['Normal']))
    elements.append(Paragraph("Teléfono: +123 456 7890 | Email: contacto@restaurante.com", styles['Normal']))
    elements.append(Spacer(1, 10))
    elements.append(Paragraph(f"<b>Factura #{factura.numero}</b>", styles['Title']))
    elements.append(Paragraph(f"Fecha: {factura.fecha.strftime('%Y-%m-%d')}", styles['Normal']))
    elements.append(Paragraph(f"Cliente: {factura.pedido.cliente.nombre}", styles['Normal']))
    elements.append(
        Paragraph(f"Estado: {'Pagado' if factura.pedido.estado == 'PAGADO' else 'Pendiente'}", styles['Normal']))
    elements.append(Spacer(1, 10))

    # Tabla de productos
    data = [["Producto", "Cantidad", "Precio Unitario", "Subtotal"]]
    for item in items:
        data.append([
            item.item_pedido.producto.nombre,
            item.cantidad,
            f"${item.item_pedido.producto.precio:.2f}",
            f"${item.subtotal:.2f}"
        ])

    table = Table(data, colWidths=[200, 80, 100, 100])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.black),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(table)

    # Totales
    elements.append(Spacer(1, 10))
    elements.append(Paragraph(f"<b>Subtotal:</b> ${factura.subtotal:.2f}", styles['Normal']))
    elements.append(Paragraph(f"<b>Impuestos:</b> ${factura.impuesto_total:.2f}", styles['Normal']))

    # Descuentos si aplica
    if factura.descuento > 0:
        elements.append(Paragraph(f"<b>Descuento aplicado:</b> ${factura.descuento:.2f}", styles['Normal']))

    # Total a pagar resaltado
    elements.append(Spacer(1, 10))
    elements.append(
        Paragraph(f"<b style='font-size:16px;'>TOTAL A PAGAR: ${factura.total:.2f}</b>", styles['Heading2']))

    elements.append(Spacer(1, 20))
    elements.append(Paragraph("Gracias por su compra. ¡Vuelva pronto!", styles['Italic']))

    # Generar PDF
    pdf.build(elements)
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Factura_{factura.numero}.pdf"'
    return response


@login_required
def crear_factura(request):
    if request.method == "POST":
        pedido_id = request.POST.get("pedido_id")
        pedido = get_object_or_404(Pedido, numero=pedido_id)  # Usar 'numero', no 'id'
        promociones_seleccionadas = request.POST.getlist("promociones")

        # 🔹 Crear y GUARDAR la factura ANTES de asignar relaciones
        factura = Factura.objects.create(pedido=pedido)

        # 🔹 Asignar ítems del pedido a la factura (NO acceder a relaciones antes de guardar)
        for item_pedido in pedido.items.all():
            ItemFactura.objects.create(
                factura=factura,
                item_pedido=item_pedido,
                cantidad=item_pedido.cantidad
            )

        # 🔹 Guardar la factura para asegurarnos de que tiene una clave primaria asignada
        factura.save()

        # 🔹 Asignar promociones a la factura (Después de guardar)
        for promo_id in promociones_seleccionadas:
            promo = get_object_or_404(Promocion, id=promo_id)
            factura.promociones.add(promo)

        # 🔹 Calcular montos finales
        factura.calcular_monto_total()
        factura.save()

        messages.success(request, "Factura creada exitosamente.")
        return redirect("factura_detalle", factura_numero=factura.numero)

    # 🔹 Obtener los pedidos pendientes y promociones activas
    pedidos = Pedido.objects.filter(estado="PENDIENTE")
    promociones = Promocion.objects.filter(activa=True)

    return render(request, "facturacion/crear_factura.html", {
        "pedidos": pedidos,
        "promociones": promociones
    })