from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.utils.timezone import now  # ✅ Importación correcta
from django.contrib import messages  # ✅ Importación correcta
from datetime import datetime
from mesas.models import Mesa, Reserva, EstadoMesa, EstadoReserva
from util.models import Cliente


@login_required
def vista_mesas(request):
    """Muestra la lista de mesas y las reservas activas (solo para empleados)."""

    estado = request.GET.get("estado")  # Obtener filtro de estado de la URL
    mesas = Mesa.objects.all()

    # Filtrar mesas según el estado si se selecciona uno
    if estado and estado in EstadoMesa.values:
        mesas = mesas.filter(estado=estado)

    # Solo los empleados pueden ver las reservas activas
    reservas = Reserva.objects.filter(estado="CONFIRMADA") if request.user.is_staff else None

    contexto = {
        "mesas": mesas,
        "reservas": reservas,
        "es_empleado": request.user.is_staff,  # 🔹 Nueva variable en el contexto
    }

    return render(request, 'mesas/ver_mesas.html', contexto)


@login_required
def reservar_mesa(request, mesa_id):
    """Permite a los clientes reservar una mesa en una fecha y hora específicas."""
    mesa = get_object_or_404(Mesa, id=mesa_id)

    # Verifica si la mesa está disponible
    if mesa.estado != EstadoMesa.LIBRE:
        messages.error(request, "❌ Esta mesa no está disponible para reservar.")
        return redirect('vista_mesas')

    # Obtiene el cliente autenticado
    cliente = Cliente.objects.filter(usuariopersonalizado=request.user).first()
    if not cliente:
        messages.error(request, "⚠️ Solo los clientes registrados pueden hacer reservas.")
        return redirect('vista_mesas')

    if request.method == "POST":
        fecha_reserva = request.POST.get("fecha_reserva")
        hora_reserva = request.POST.get("hora_reserva")

        if not fecha_reserva or not hora_reserva:
            messages.error(request, "⚠️ Debes seleccionar una fecha y hora válidas.")
            return redirect('reservar_mesa', mesa_id=mesa.id)

        horario_inicio = datetime.strptime(f"{fecha_reserva} {hora_reserva}", "%Y-%m-%d %H:%M")

        # Crear la reserva
        reserva = Reserva.objects.create(
            identificador=f"RES-{mesa.id}-{horario_inicio.strftime('%Y%m%d%H%M')}",
            cliente=cliente,
            mesa=mesa,
            cantidad_personas=mesa.numero_asientos,
            fecha_reserva=fecha_reserva,
            horario_inicio=horario_inicio,
            estado="CONFIRMADA"
        )

        # Actualizar el estado de la mesa a RESERVADA
        mesa.estado = EstadoMesa.RESERVADA
        mesa.save()

        messages.success(request, f"✅ Reserva confirmada para la Mesa #{mesa.identificador}.")
        return redirect('vista_mesas')

    return render(request, "mesas/reservar_mesa.html", {"mesa": mesa})



@login_required
def cambiar_estado_mesa(request, mesa_id):
    """Permite cambiar el estado de una mesa (Solo empleados)."""
    mesa = get_object_or_404(Mesa, id=mesa_id)

    if not request.user.is_staff:  # Solo empleados pueden cambiar estado
        messages.error(request, "No tienes permiso para cambiar el estado de la mesa.")
        return redirect("vista_mesas")

    if request.method == "POST":
        nuevo_estado = request.POST.get("nuevo_estado")

        if nuevo_estado in EstadoMesa.values:
            mesa.estado = nuevo_estado
            mesa.save()
            messages.success(request, f"Estado de la Mesa #{mesa.identificador} actualizado a {nuevo_estado}.")
        else:
            messages.error(request, "Estado no válido.")

    return redirect("vista_mesas")

@login_required
def ver_reservas(request):
    """Muestra todas las reservas activas de un cliente."""
    cliente = Cliente.objects.filter(usuariopersonalizado=request.user).first()

    if not cliente:
        messages.error(request, "Debes ser un cliente registrado para ver tus reservas.")
        return redirect('vista_cliente')

    reservas = Reserva.objects.filter(cliente=cliente, estado=EstadoReserva.CONFIRMADA).order_by('-fecha_reserva')

    return render(request, 'mesas/ver_reservas.html', {'reservas': reservas})

@login_required
def cancelar_reserva(request, reserva_id):
    """Cancela una reserva si aún está confirmada."""
    reserva = get_object_or_404(Reserva, id=reserva_id)

    if reserva.estado == EstadoReserva.CONFIRMADA:
        reserva.estado = EstadoReserva.CANCELADA
        reserva.save()
        messages.success(request, f"✅ La reserva {reserva.identificador} ha sido cancelada correctamente.")

    return redirect('ver_reservas')