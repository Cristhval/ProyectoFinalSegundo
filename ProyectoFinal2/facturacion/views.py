import requests
from django.shortcuts import render
from .models import Promocion
from django.contrib import messages
from facturacion.models import Factura, PagoEfectivo, PagoTarjeta, PagoTransferencia
from util.models import Cliente
from django.contrib.auth.decorators import login_required

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
def vista_metodos_pago(request):
    try:
        cliente = request.user.cliente  # Accede al cliente vinculado al usuario

        # Obtener las facturas del cliente
        facturas = Factura.objects.filter(pedido__cliente=cliente)

        # Filtrar los métodos de pago utilizados en las facturas del cliente
        pagos_efectivo = PagoEfectivo.objects.filter(factura__in=facturas)
        pagos_tarjeta = PagoTarjeta.objects.filter(factura__in=facturas)
        pagos_transferencia = PagoTransferencia.objects.filter(factura__in=facturas)

    except Cliente.DoesNotExist:
        facturas = None
        pagos_efectivo = None
        pagos_tarjeta = None
        pagos_transferencia = None

    context = {
        'facturas': facturas,
        'pagos_efectivo': pagos_efectivo,
        'pagos_tarjeta': pagos_tarjeta,
        'pagos_transferencia': pagos_transferencia,
    }

    return render(request, 'facturacion/metodos_pago.html', context)