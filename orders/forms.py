from django import forms
from .models import Order
from django.contrib.auth.models import User
class OrderCreateForm(forms.ModelForm):
    user=User.objects.only('username')
    class Meta:
        model = Order
        # fields = ['first_name', 'last_name', 'email', 'address',
        # 'postal_code', 'city']
        fields=('montant_recu','Mode_de_paiment')