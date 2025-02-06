from django.contrib import admin
from .models import Menu, Categoria, Producto
from util.models import Impuesto

# --- CONFIGURACIÓN PARA MENU ---
@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'estado')
    search_fields = ('nombre',)
    list_filter = ('estado',)

# --- CONFIGURACIÓN PARA CATEGORIA ---
@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'menu')
    search_fields = ('nombre', 'menu__nombre')
    list_filter = ('menu',)

# --- CONFIGURACIÓN PARA PRODUCTO ---
@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'precio', 'disponibilidad', 'categoria')
    search_fields = ('nombre', 'categoria__nombre')
    list_filter = ('disponibilidad', 'categoria')
    filter_horizontal = ('impuestos',)  # ✅ Permite agregar y quitar impuestos en el admin
