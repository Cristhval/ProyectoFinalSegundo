from django.contrib import admin
from .models import Menu, Categoria, Producto

# Configuración de Menús en Admin
@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'estado')
    list_filter = ('estado',)
    search_fields = ('nombre',)
    ordering = ('nombre',)

# Configuración de Categorías en Admin
@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'menu')
    list_filter = ('menu',)
    search_fields = ('nombre', 'menu__nombre')
    ordering = ('nombre',)

# Configuración de Productos en Admin
@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'descripcion', 'precio', 'disponibilidad', 'categoria')
    list_filter = ('categoria', 'disponibilidad')
    search_fields = ('nombre', 'categoria__nombre')
    ordering = ('nombre',)
    list_editable = ('precio', 'disponibilidad')