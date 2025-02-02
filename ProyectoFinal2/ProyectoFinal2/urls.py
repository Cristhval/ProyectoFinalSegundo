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

from inventario.views import vista_inventario
from menus.views import ver_menu
from mesas.views import vista_mesas
from util import views
from pedidos.views import detalle_pedido, ver_pokemon_pedido, crear_pedido, lista_pedidos, editar_pedido, ver_pedidos
from facturacion.views import (
    promociones_por_clima, vista_metodos_pago, lista_facturas,
    detalle_factura, descargar_factura_pdf, crear_factura
)

urlpatterns = [
    # 🔹 Administración
    path('admin/', admin.site.urls),

    # 🔹 Páginas de inicio y autenticación
    path('', views.vista_publica, name='public_home'),  # Página pública
    path('home/', views.home, name='home'),  # Redirigir usuarios autenticados
    path('login/', LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),

    # 📌 Vistas del cliente
    path('cliente/', views.vista_cliente, name='vista_cliente'),
    path('cliente/pedidos/', views.vista_pedidos_cliente, name='vista_pedidos_cliente'),
    path('cliente/metodos-pago/<int:factura_numero>/', vista_metodos_pago, name='vista_metodos_pago'),

    # 📌 Detalles de pedidos
    path('detalle/<int:pedido_numero>/', detalle_pedido, name='detalle_pedido'),
    path('pedido/<int:pedido_numero>/pokemon/', ver_pokemon_pedido, name='ver_pokemon_pedido'),

    # 📌 Vistas de empleados y administradores
    path('empleado/', views.vista_empleado, name='vista_empleado'),
    path('admin-dashboard/', views.vista_admin, name='vista_admin'),

    # 📌 Funcionalidades adicionales
    path('promociones/', promociones_por_clima, name='promociones'),

    # 📌 Facturación
    path('facturas/', lista_facturas, name='factura_lista'),
    path('factura/<int:factura_numero>/', detalle_factura, name='factura_detalle'),
    path('factura/<int:factura_numero>/descargar/', descargar_factura_pdf, name='descargar_factura_pdf'),
    path('factura/crear/', crear_factura, name='crear_factura'),

    # 📌 Gestión del menú, inventario y mesas
    path('menu/', ver_menu, name='ver_menu'),
    path('inventario/', vista_inventario, name='vista_inventario'),
    path('mesas/', vista_mesas, name='vista_mesas'),

    # 📌 Creación de pedidos (solo con clientes registrados)
    path('pedidos/crear/', crear_pedido, name='crear_pedido'),  # 🔹 Ruta principal
    path('pedidos/crear/<int:producto_id>/', crear_pedido, name='crear_pedido_por_producto'),
    path('pedidos/', lista_pedidos, name='lista_pedidos'),
    path('pedidos/editar/<int:pedido_numero>/', editar_pedido, name='editar_pedido'),
    path('pedidos/', ver_pedidos, name='ver_pedidos'),
]


