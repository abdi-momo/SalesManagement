from django.contrib import admin
from .models import Category, Product

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['nom', 'slug']
    prepopulated_fields = {'slug': ('nom',)}

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['libelle', 'slug', 'prix','quantite', 'date_creation', 'date_creation']
    list_filter = ['categorie','date_creation', 'date_modification']
    list_editable = ['prix', 'quantite']
    prepopulated_fields = {'slug': ('libelle',)}