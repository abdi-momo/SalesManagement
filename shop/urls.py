from django.urls import path
from . import views
from .views import AccountListView
app_name = 'shop'
urlpatterns = [
    path('', views.product_list, name='product_list'),
    path('<slug:category_slug>/', views.product_list, name='product_list_by_category'),
    path('<int:id>/<slug:slug>/', views.product_detail, name='product_detail'),
    # path('add/<int:id>/add_to_cart/', views.product_detail, name='add_to_cart'),
    path('user/add_user/', views.add_user_view, name='add_user'),
    path("account/signup/", views.signup, name="signup"),
    path("account/signin/", views.signin, name="signin"),
    path("account/logout/", views.logout_view, name="logout"),
    path("products/create/", views.create_product, name="create-product"),
    path("products/list/", views.products_ListView, name="products_List"),
    path('product/<int:pk>/edit/', views.ProductUpdateView, name='product_update'),
    path("category/create/", views.create_category, name="create-category"),
    path('category/<int:pk>/edit/', views.CategoryUpdateView, name='category_update'),
    path('category/list', views.CategorieList, name='listeCategory'),
    path('accounts/', AccountListView.as_view(), name='all_accounts'),
]