from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import UsuarioPersonalizado

class ClienteRegistroForm(UserCreationForm):
    email = forms.EmailField(required=True, help_text="Requerido. Introduce una dirección de correo válida.")
    nombre = forms.CharField(max_length=50, required=True)
    apellido = forms.CharField(max_length=50, required=True)
    telefono = forms.CharField(max_length=15, required=True)

    class Meta:
        model = UsuarioPersonalizado  # Usa el modelo personalizado
        fields = ["username", "email", "nombre", "apellido", "telefono", "password1", "password2"]
