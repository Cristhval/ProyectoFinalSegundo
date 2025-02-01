from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    UsuarioPersonalizado, Cliente, Mesero, PersonalCocina, Administrador,
    Proveedor
)


# Configuración para UsuarioPersonalizado en el Admin de Django
class UsuarioPersonalizadoAdmin(UserAdmin):
    model = UsuarioPersonalizado
    list_display = ('username', 'email', 'tipo_usuario', 'is_active', 'is_staff', 'is_superuser')
    list_filter = ('tipo_usuario', 'is_active', 'is_staff')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Información Personal', {'fields': ('first_name', 'last_name', 'email')}),
        ('Roles y Permisos', {'fields': ('tipo_usuario', 'is_staff', 'is_active', 'groups', 'user_permissions')}),
        ('Fechas Importantes', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'tipo_usuario', 'is_staff', 'is_active')}
        ),
    )
    search_fields = ('username', 'email')
    ordering = ('username',)


# Configuración para Cliente en el Admin
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'apellido', 'cedula', 'email', 'telefono', 'activo')
    search_fields = ('nombre', 'apellido', 'cedula', 'email')
    list_filter = ('activo',)


# Configuración para Administrador en el Admin
class AdministradorAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'apellido', 'cedula', 'email', 'telefono', 'rol')
    search_fields = ('nombre', 'apellido', 'cedula', 'email')
    list_filter = ('rol',)


# Configuración para Mesero en el Admin
class MeseroAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'apellido', 'cedula', 'email', 'telefono', 'esta_ocupado', 'pedidos_atendidos')
    search_fields = ('nombre', 'apellido', 'cedula', 'email')
    list_filter = ('esta_ocupado',)


# Configuración para Personal de Cocina en el Admin
class PersonalCocinaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'apellido', 'cedula', 'email', 'telefono', 'esta_cocinando')
    search_fields = ('nombre', 'apellido', 'cedula', 'email')
    list_filter = ('esta_cocinando',)


# Configuración para Proveedor en el Admin
class ProveedorAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'contacto', 'email', 'direccion')
    search_fields = ('nombre', 'contacto', 'email')




# Registrar los modelos en el panel de administración
admin.site.register(UsuarioPersonalizado, UsuarioPersonalizadoAdmin)
admin.site.register(Cliente, ClienteAdmin)
admin.site.register(Administrador, AdministradorAdmin)
admin.site.register(Mesero, MeseroAdmin)
admin.site.register(PersonalCocina, PersonalCocinaAdmin)
admin.site.register(Proveedor, ProveedorAdmin)

