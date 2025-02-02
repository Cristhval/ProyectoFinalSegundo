from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    UsuarioPersonalizado, Cliente, Mesero, PersonalCocina, Administrador,
    Proveedor, Impuesto
)

# --- CONFIGURACIÓN DEL ADMIN DE USUARIO PERSONALIZADO ---
@admin.register(UsuarioPersonalizado)
class UsuarioPersonalizadoAdmin(UserAdmin):
    list_display = ('username', 'tipo_usuario', 'is_active', 'is_staff')
    list_filter = ('tipo_usuario', 'is_staff', 'is_active')
    search_fields = ('username', 'email')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Información Personal', {'fields': ('first_name', 'last_name', 'email')}),
        ('Tipo de Usuario', {'fields': ('tipo_usuario', 'cliente', 'mesero', 'personal_cocina', 'administrador')}),
        ('Permisos', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Fechas Importantes', {'fields': ('last_login', 'date_joined')}),
    )

# --- CONFIGURACIÓN PARA CLIENTE ---
@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'apellido', 'cedula', 'telefono', 'email', 'activo')
    search_fields = ('nombre', 'apellido', 'cedula')
    list_filter = ('activo',)

# --- CONFIGURACIÓN PARA MESERO ---
@admin.register(Mesero)
class MeseroAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'apellido', 'cedula', 'telefono', 'rol', 'esta_ocupado', 'pedidos_atendidos')
    search_fields = ('nombre', 'apellido', 'cedula')
    list_filter = ('rol', 'esta_ocupado')

# --- CONFIGURACIÓN PARA PERSONAL DE COCINA ---
@admin.register(PersonalCocina)
class PersonalCocinaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'apellido', 'cedula', 'telefono', 'rol', 'esta_cocinando')
    search_fields = ('nombre', 'apellido', 'cedula')
    list_filter = ('rol', 'esta_cocinando')

# --- CONFIGURACIÓN PARA ADMINISTRADOR ---
@admin.register(Administrador)
class AdministradorAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'apellido', 'cedula', 'telefono', 'rol')
    search_fields = ('nombre', 'apellido', 'cedula')
    list_filter = ('rol',)

# --- CONFIGURACIÓN PARA PROVEEDOR ---
@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'email', 'direccion', 'telefono_contacto')
    search_fields = ('nombre', 'email', 'telefono_contacto')

# --- CONFIGURACIÓN PARA IMPUESTO ---
@admin.register(Impuesto)
class ImpuestoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'porcentaje', 'descripcion')
    search_fields = ('nombre',)
