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
from pedidos.views import detalle_pedido, ver_pokemon_pedido
from facturacion.views import promociones_por_clima, vista_metodos_pago, lista_facturas, detalle_factura, \
    descargar_factura_pdf

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.vista_publica, name='public_home'),  # Página pública
    path('home/', views.home, name='home'),  # Redirigir usuarios autenticados

    # 📌 Vistas del cliente
    path('cliente/', views.vista_cliente, name='vista_cliente'),
    path('cliente/pedidos/', views.vista_pedidos_cliente, name='vista_pedidos_cliente'),
    path('cliente/metodos-pago/<int:factura_numero>/', vista_metodos_pago, name='vista_metodos_pago'),

    path('detalle/<int:pedido_numero>/', detalle_pedido, name='detalle_pedido'),
    path('pedido/<int:pedido_numero>/pokemon/', ver_pokemon_pedido, name='ver_pokemon_pedido'),

    # 📌 Vistas de empleado y admin
    path('empleado/', views.vista_empleado, name='vista_empleado'),
    path('admin-dashboard/', views.vista_admin, name='vista_admin'),

    # Login y Logout
    path('login/', LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),

    # Funcionalidades adicionales
    path('promociones/', promociones_por_clima, name='promociones'),
    path('facturas/', lista_facturas, name='factura_lista'),
    path('factura/<int:factura_numero>/', detalle_factura, name='factura_detalle'),
    path('factura/<int:factura_numero>/descargar/', descargar_factura_pdf, name='descargar_factura_pdf'),

]


