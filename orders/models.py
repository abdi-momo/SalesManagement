from django.db import models
from shop.models import Product
from datetime import datetime
from django.contrib.auth.models import User
class Order(models.Model):
    payment_list = (('Espece','Espece'),
                    ('Chèque','Cheque'),
                    ('Carte de crédit', 'Carte de crédit'),
                    ('Carte de débit','Carte de débit'),
                    ('A crédit','A crédit'),)
    
    utilisateur = models.ForeignKey(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=50, blank=True)
    last_name = models.CharField(max_length=50,  blank=True)
    email = models.EmailField()
    address = models.CharField(max_length=250, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    city = models.CharField(max_length=100,  blank=True)
    date_creation = models.DateField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    paid = models.BooleanField(default=True)
    montant_recu = models.DecimalField(max_digits=10, decimal_places=2)
    Mode_de_paiment = models.CharField(choices=payment_list, max_length=15)

    class Meta:
        ordering = ('-date_creation',)
    def __str__(self):
        return 'Order {}'.format(self.id)

    def get_total_cost(self):
        return sum(item.get_cost() for item in self.items.all())

    def montant_restant(self):
        return self.montant_recu - self.get_total_cost()

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='order_items', on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)
    tva = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    def __str__(self):
        return '{}'.format(self.id)
    def get_cost(self):
        return self.price * self.quantity+(self.price * self.quantity)*self.tva