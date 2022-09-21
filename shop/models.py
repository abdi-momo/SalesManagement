from django.db import models
from django.urls import reverse
from decimal import Decimal

class Category(models.Model):
    nom = models.CharField(max_length=200, db_index=True)
    slug = models.SlugField(max_length=200, unique=True)
    class Meta:
        ordering = ('nom',)
        verbose_name = 'category'
        verbose_name_plural = 'categories'
    def __str__(self):
        return self.nom

    def get_absolute_url(self):
        return reverse('shop:product_list_by_category',
                       args=[self.slug])

class Product(models.Model):
    product_unit = (('L', 'Litre(s)'),
                    ('Kg', 'Kilogramme(s)'),
                    ('Crt', 'Carton(s)'),
                    ('Blle', 'Bouteille(s)'),
                    ('Bte', 'Boite(s)'),
                    ('Sc', 'Sac(s)'),
                    ('Ut','Unité'),)
    taxe_rate = (
        (1,0.1),
        (2,0.07),
        (3,0.05),
        (4,0.03),
        (5,0.00),)
    categorie = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)
    code=models.CharField(max_length=20, unique=True, null=True)
    libelle = models.CharField(max_length=200, db_index=True)
    quantite=models.IntegerField(blank=True, default=0)
    unite=models.CharField(choices=product_unit, max_length=15)
    slug = models.SlugField(max_length=200, db_index=True)
    image = models.ImageField(upload_to='products/%Y/%m/%d', blank=True)
    description = models.TextField(blank=True)
    cout_de_revient=models.DecimalField(max_digits=10, decimal_places=2)
    prix = models.DecimalField(max_digits=10, decimal_places=2)
    available = models.BooleanField(default=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    TVA = models.DecimalField(choices=taxe_rate, max_digits=10, decimal_places=2)
    class Meta:
        ordering = ('libelle',)
        index_together = (('id', 'slug'),)

    def save(self, TAVA=Decimal('0.00'), *args, **kwargs):
        if self.TVA==1:
            self.TVA=Decimal(0.10)
        elif self.TVA==2:
            self.TVA=Decimal(0.07)
        elif self.TVA==3:
            self.TVA=Decimal(0.05)
        elif self.TVA==4:
            self.TVA=Decimal(0.03)
        else:
            self.TVA=Decimal(0.00)
        super(Product, self).save(*args,**kwargs)

    def __str__(self):
        return self.libelle
    def get_cost_margin(self):
       return self.prix - self.cout_de_revient

    def get_absolute_url(self):
        return reverse('shop:product_detail',
                       args=[self.id, self.slug])
