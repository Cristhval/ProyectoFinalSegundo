
from django.contrib import admin
from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from inventario.views import vista_inventario, gestionar_inventario, generar_reporte_bodega, generar_reporte_consumo
from menus.views import ver_menu
from mesas.views import vista_mesas, reservar_mesa, cambiar_estado_mesa, ver_reservas, cancelar_reserva
from util import views
from pedidos.views import detalle_pedido, ver_pokemon_pedido, crear_pedido, lista_pedidos, editar_pedido, ver_pedidos
from facturacion.views import (
    promociones_por_clima, vista_metodos_pago, lista_facturas,
    detalle_factura, descargar_factura_pdf, crear_factura
)
from estadisticas.views import dashboard_estadisticas, exportar_estadisticas_pdf
from util.views import registro_cliente

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

    # 📌 Estadísticas
    path("estadisticas/", dashboard_estadisticas, name="dashboard-estadisticas"),
    path('dashboard/', dashboard_estadisticas, name='dashboard_estadisticas'),
    path('exportar/<str:fecha_inicio>/<str:fecha_fin>/', exportar_estadisticas_pdf, name='exportar_estadisticas_pdf'),
    path("registro/", registro_cliente, name="registro_cliente"),

    path('inventario/gestionar/', gestionar_inventario, name='gestionar_inventario'),
    path('inventario/reporte-bodega/', generar_reporte_bodega, name='generar_reporte_bodega'),
    path('inventario/reporte-consumo/', generar_reporte_consumo, name='generar_reporte_consumo'),

    path('reservar/<int:mesa_id>/', reservar_mesa, name='reservar_mesa'),
    path('cambiar_estado/<int:mesa_id>/', cambiar_estado_mesa, name='cambiar_estado_mesa'),

    path('reservas/', ver_reservas, name='ver_reservas'),  # 🔹 Ver reservas activas
    path('cancelar_reserva/<int:reserva_id>/', cancelar_reserva, name='cancelar_reserva'),

    path('reservar/<int:mesa_id>/', reservar_mesa, name='reservar_mesa'),
]



