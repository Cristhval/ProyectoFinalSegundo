from collections import defaultdict

import requests
from django.db import transaction
from django.shortcuts import render, get_object_or_404, redirect

from pedidos.models import Pedido
from util.models import Cliente
from .models import Promocion, ItemFactura
from django.contrib import messages
from facturacion.models import Factura, PagoEfectivo, PagoTarjeta, PagoTransferencia
from django.contrib.auth.decorators import login_required
from reportlab.lib.pagesizes import letter
from django.http import HttpResponse, JsonResponse
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
    factura = get_object_or_404(Factura, numero=factura_numero)

    # Agrupar productos para evitar duplicaciones
    productos_agrupados = {}
    for item in factura.items.all():
        nombre_producto = item.item_pedido.producto.nombre
        if nombre_producto in productos_agrupados:
            productos_agrupados[nombre_producto]["cantidad"] += item.cantidad
            productos_agrupados[nombre_producto]["subtotal"] += item.subtotal
        else:
            productos_agrupados[nombre_producto] = {
                "cantidad": item.cantidad,
                "precio": item.item_pedido.producto.precio,
                "subtotal": item.subtotal
            }

    # Obtener pagos asociados
    pagos = []
    pagos.extend(PagoEfectivo.objects.filter(factura=factura).values("monto_pagado"))
    pagos.extend(PagoTarjeta.objects.filter(factura=factura).values("monto_pagado"))
    pagos.extend(PagoTransferencia.objects.filter(factura=factura).values("monto_pagado"))

    # Convertir pagos en un formato adecuado para el template
    pagos_finales = []
    for pago in pagos:
        metodo = "Efectivo" if "cambio" in pago else "Tarjeta" if "numero_tarjeta" in pago else "Transferencia"
        pagos_finales.append({"metodo": metodo, "monto": pago["monto_pagado"]})

    return render(request, "facturacion/factura_detalle.html", {
        "factura": factura,
        "productos_agrupados": productos_agrupados,
        "pagos": pagos_finales
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
        pedido = get_object_or_404(Pedido, numero=pedido_id)
        promociones_seleccionadas = request.POST.getlist("promociones")
        metodo_pago = request.POST.get("metodo_pago")

        # Obtener monto pagado si es efectivo
        monto_pagado = float(request.POST.get("monto_pagado", "0") or 0)

        # Calcular el subtotal antes de aplicar impuestos y descuentos
        subtotal_sin_descuento = sum(item.cantidad * item.producto.precio for item in pedido.items.all())

        # Calcular descuentos
        descuento_total = 0.0
        for promo in Promocion.objects.filter(id__in=promociones_seleccionadas):
            descuento_total += subtotal_sin_descuento * (promo.porcentaje_descuento / 100)

        # Aplicar descuento antes de calcular el IVA
        subtotal_con_descuento = subtotal_sin_descuento - descuento_total

        # Calcular impuestos (IVA del 15%)
        IVA = 0.15
        impuesto_total = round(subtotal_con_descuento * IVA, 2)

        # Calcular total final
        total_a_pagar = round(subtotal_con_descuento + impuesto_total, 2)

        # Crear factura y guardar valores correctos
        factura = Factura.objects.create(
            pedido=pedido,
            subtotal=round(subtotal_sin_descuento, 2),
            descuento=round(descuento_total, 2),
            impuesto_total=impuesto_total,
            total=total_a_pagar
        )

        # Agregar promociones a la factura
        for promo_id in promociones_seleccionadas:
            promo = get_object_or_404(Promocion, id=promo_id)
            factura.promociones.add(promo)

        # Manejar métodos de pago
        cambio = max(monto_pagado - total_a_pagar, 0)
        if metodo_pago == "efectivo":
            factura.metodo_pago_efectivo = PagoEfectivo.objects.create(
                monto_pagado=monto_pagado, cuenta_por_cobrar=0, cambio=cambio
            )
        elif metodo_pago == "tarjeta":
            factura.metodo_pago_tarjeta = PagoTarjeta.objects.create(
                monto_pagado=total_a_pagar, cuenta_por_cobrar=0, numero_tarjeta="XXXX-XXXX-XXXX-0000",
                titular="Cliente", vencimiento="2025-12-31"
            )
        elif metodo_pago == "transferencia":
            factura.metodo_pago_transferencia = PagoTransferencia.objects.create(
                monto_pagado=total_a_pagar, cuenta_por_cobrar=0, numero_transferencia="123456", banco_origen="Banco XYZ"
            )

        factura.save()
        messages.success(request, "✅ Factura creada exitosamente.")
        return redirect("factura_detalle", factura_numero=factura.numero)

    pedidos = Pedido.objects.filter(estado="PENDIENTE")
    promociones = Promocion.objects.filter(activa=True)

    return render(request, "facturacion/crear_factura.html", {
        "pedidos": pedidos,
        "promociones": promociones
    })

def obtener_detalle_pedido(request, pedido_id):
    """ Devuelve los productos de un pedido en JSON """
    pedido = get_object_or_404(Pedido, numero=pedido_id)

    productos = [
        {
            "nombre": item.producto.nombre,
            "precio": float(item.producto.precio),
            "cantidad": item.cantidad,
            "subtotal": round(item.producto.precio * item.cantidad, 2)
        }
        for item in pedido.items.all()
    ]

    return JsonResponse({"cliente": pedido.cliente.nombre, "productos": productos})


@login_required
def lista_facturas(request):
    """Muestra el historial de facturas con opción de filtrar por fecha, monto, cliente y estado."""

    facturas = Factura.objects.all().order_by('-fecha')

    # Obtener parámetros de filtrado desde la solicitud GET
    fecha_inicio = request.GET.get("fecha_inicio")
    fecha_fin = request.GET.get("fecha_fin")
    monto_min = request.GET.get("monto_min")
    monto_max = request.GET.get("monto_max")
    cliente_id = request.GET.get("cliente_id")
    estado = request.GET.get("estado")  # Nuevo filtro por estado

    # Aplicar filtros si se ingresaron valores en el formulario
    if fecha_inicio and fecha_fin:
        facturas = facturas.filter(fecha__range=[fecha_inicio, fecha_fin])

    if monto_min:
        facturas = facturas.filter(total__gte=float(monto_min))

    if monto_max:
        facturas = facturas.filter(total__lte=float(monto_max))

    if cliente_id:
        facturas = facturas.filter(pedido__cliente_id=cliente_id)

    if estado in ["PENDIENTE", "PAGADO"]:
        facturas = facturas.filter(pedido__estado=estado)

    # Obtener lista de clientes para el filtro
    clientes = Cliente.objects.all()

    return render(request, 'facturacion/factura_lista.html', {
        'facturas': facturas,
        'clientes': clientes,
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin,
        'monto_min': monto_min,
        'monto_max': monto_max,
        'cliente_id': cliente_id,
        'estado': estado  # Pasar el estado al template
    })

def editar_factura(request, factura_numero):
    """Permite editar el estado de una factura y modificar promociones."""
    factura = get_object_or_404(Factura, numero=factura_numero)

    if request.method == "POST":
        # Actualizar estado de la factura
        nuevo_estado = request.POST.get("estado")
        if nuevo_estado in ["PENDIENTE", "PAGADO"]:
            factura.pedido.estado = nuevo_estado
            factura.pedido.save()

        # Actualizar promociones
        promociones_seleccionadas = request.POST.getlist("promociones")
        factura.promociones.clear()
        for promo_id in promociones_seleccionadas:
            promo = get_object_or_404(Promocion, id=promo_id)
            factura.promociones.add(promo)

        factura.save()
        messages.success(request, "✅ Factura actualizada correctamente.")
        return redirect("factura_detalle", factura_numero=factura.numero)

    promociones = Promocion.objects.filter(activa=True)

    return render(request, "facturacion/editar_factura.html", {
        "factura": factura,
        "promociones": promociones
    })