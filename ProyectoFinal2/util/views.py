from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse
from django.contrib.auth import logout
from django.views import View

class CustomLoginView(LoginView):
    template_name = "registration/login.html"
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy('home')

class CustomLogoutView(View):
    def post(self, request):
        logout(request)
        return redirect(reverse('public_home'))
 #Vista para usuarios NO autenticados (página de inicio pública)
def vista_publica(request):
    return render(request, 'public_home.html')

# Vista para el cliente
@login_required
def vista_cliente(request):
    if request.user.es_cliente():
        return render(request, 'cliente/dashboard.html')
    return redirect('login')

# Vista para el empleado (mesero, personal de cocina)
@login_required
def vista_empleado(request):
    if request.user.es_empleado():
        return render(request, 'empleado/dashboard.html')
    return redirect('login')

# Vista para el administrador
@login_required
def vista_admin(request):
    if request.user.es_admin():
        return render(request, 'admin/dashboard.html')
    return redirect('login')

# Vista para usuarios no autenticados
@login_required
def home(request):
    user = request.user

    # Redirigir según el tipo de usuario
    if user.tipo_usuario == 'Cliente':
        return redirect(reverse('vista_cliente'))
    elif user.tipo_usuario == 'Empleado':
        return redirect(reverse('vista_empleado'))
    elif user.tipo_usuario == 'Administrador':
        return redirect(reverse('vista_admin'))

    # Si el usuario no tiene tipo definido, enviarlo a la página pública
    return redirect(reverse('public_home'))