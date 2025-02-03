from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import Group
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse
from django.contrib.auth import logout, login
from django.views import View
from pedidos.models import Pedido
from util.forms import ClienteRegistroForm
from util.models import Cliente
from facturacion.models import Promocion, Factura, ItemFactura


class CustomLoginView(LoginView):
    template_name = "registration/login.html"
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy('home')

class CustomLogoutView(View):
    def post(self, request):
        logout(request)
        return redirect(reverse('public_home'))

# Vista para usuarios NO autenticados (página de inicio pública)
def vista_publica(request):
    return render(request, 'public_home.html')

# Vista para el cliente con facturas incluidas en el contexto
@login_required
def vista_cliente(request):
    if request.user.es_cliente():
        cliente = request.user.cliente
        facturas = Factura.objects.filter(pedido__cliente=cliente).order_by('-fecha')
        return render(request, 'cliente/dashboard.html', {
            "usuario": request.user,   # 🔹 Pasamos el usuario al template
            "facturas": facturas
        })
    return redirect('login')

# Vista para el empleado (mesero, personal de cocina)
@login_required
def vista_empleado(request):
    if request.user.tipo_usuario in ['Mesero', 'Cocinero']:  # 🔹 Verificamos el tipo correctamente
        return render(request, 'empleado/dashboard.html')
    return redirect('login')

# Vista para el administrador con estadísticas
@login_required
def vista_admin(request):
    if request.user.es_admin():
        context = {
            "total_pedidos": Pedido.objects.count(),
            "total_clientes": Cliente.objects.count(),
            "total_promociones": Promocion.objects.filter(activa=True).count(),
            "total_facturas": Factura.objects.count(),
        }
        return render(request, 'admin/dashboard.html', context)
    return redirect('login')

# Vista para usuarios autenticados, redirige al dashboard correspondiente
@login_required
def home(request):
    user = request.user

    # 🔹 Corregimos la lógica de redirección
    if user.tipo_usuario == 'Cliente':
        return redirect(reverse('vista_cliente'))
    elif user.tipo_usuario == 'Mesero' or user.tipo_usuario == 'Cocinero':  # 🔹 Corregido
        return redirect(reverse('vista_empleado'))
    elif user.tipo_usuario == 'Administrador':
        return redirect(reverse('vista_admin'))

    # Si el usuario no tiene tipo definido, enviarlo a la página pública
    return redirect(reverse('public_home'))


@login_required
def vista_pedidos_cliente(request):
    cliente = getattr(request.user, 'cliente', None)

    if cliente:
        pedidos = Pedido.objects.filter(cliente=cliente).order_by('-fecha_actual')  # Ordenar por fecha
    else:
        pedidos = []  # Asegurar que pedidos no sea None

    return render(request, 'cliente/pedidos.html', {'pedidos': pedidos})



def registro_cliente(request):
    if request.method == "POST":
        form = ClienteRegistroForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.tipo_usuario = "Cliente"  # Asegurar que el usuario sea cliente
            user.save()
            grupo_cliente, created = Group.objects.get_or_create(name="Cliente")
            user.groups.add(grupo_cliente)  # Agregar al grupo "Cliente"
            login(request, user)  # Iniciar sesión después del registro
            return redirect("home")  # Redirigir a la página principal
    else:
        form = ClienteRegistroForm()

    return render(request, "registration/registro_cliente.html", {"form": form})