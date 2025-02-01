from django.contrib import admin
from.models import Impuesto

# Configuración para Impuesto en el Admin
class ImpuestoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'porcentaje', 'descripcion')
    search_fields = ('nombre',)


admin.site.register(Impuesto, ImpuestoAdmin)