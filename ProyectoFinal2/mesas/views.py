from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from mesas.models import Mesa

@login_required
def vista_mesas(request):
    mesas = Mesa.objects.all()
    return render(request, 'mesas/ver_mesas.html', {'mesas': mesas})
