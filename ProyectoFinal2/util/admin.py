from django.contrib import admin
from .models import (
    Cliente, Mesero, PersonalCocina, Administrador, Proveedor, Usuario, Impuesto
)

# Configuración de Cliente en Admin
@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'apellido', 'cedula', 'telefono', 'email', 'activo')
    search_fields = ('nombre', 'apellido', 'cedula')
    list_filter = ('activo',)
    ordering = ('apellido',)
    filter_horizontal = ('historial_pedidos',)  # Para mejor gestión de pedidos

# Configuración de Mesero en Admin
@admin.register(Mesero)
class MeseroAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'apellido', 'cedula', 'identificacion', 'esta_ocupado', 'pedidos_atendidos')
    search_fields = ('nombre', 'apellido', 'cedula', 'identificacion')
    list_filter = ('esta_ocupado',)
    ordering = ('apellido',)

# Configuración de PersonalCocina en Admin
@admin.register(PersonalCocina)
class PersonalCocinaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'apellido', 'cedula', 'identificacion', 'esta_cocinando')
    search_fields = ('nombre', 'apellido', 'cedula', 'identificacion')
    list_filter = ('esta_cocinando',)
    ordering = ('apellido',)

# Configuración de Administrador en Admin
@admin.register(Administrador)
class AdministradorAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'apellido', 'cedula', 'rol')
    search_fields = ('nombre', 'apellido', 'cedula')
    ordering = ('apellido',)

# Configuración de Proveedor en Admin
@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'contacto', 'email', 'direccion')
    search_fields = ('nombre', 'contacto', 'email')
    ordering = ('nombre',)

# Configuración de Usuario en Admin
@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'rol', 'email')
    search_fields = ('nombre', 'email')
    ordering = ('nombre',)

# Configuración de Impuesto en Admin
@admin.register(Impuesto)
class ImpuestoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'porcentaje', 'descripcion')
    search_fields = ('nombre',)
    ordering = ('nombre',)
