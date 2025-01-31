"""
URL configuration for ProyectoFinal2 project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from util import views
from pedidos.views import pedido_con_pokemon
from facturacion.views import promociones_por_clima
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.vista_publica, name='public_home'),  # Página pública
    path('home/', views.home, name='home'),  # Redirigir usuarios autenticados

    # Vistas para diferentes usuarios
    path('cliente/', views.vista_cliente, name='vista_cliente'),
    path('empleado/', views.vista_empleado, name='vista_empleado'),
    path('admin-dashboard/', views.vista_admin, name='vista_admin'),

    # Login y Logout
    path('login/', LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('pedido-pokemon/', pedido_con_pokemon, name='pedido_pokemon'),
    path('promociones/', promociones_por_clima, name='promociones'),
]
