from django.urls import path
from . import views
app_name = 'orders'
urlpatterns = [
    path('create/', views.order_create, name='order_create'),
    path('admin/order/<int:order_id>/', views.admin_order_detail, name='admin_order_detail'),
    path('admin/order/<int:order_id>/pdf/', views.admin_order_pdf, name='admin_order_pdf'),
    path('daily_report/', views.daily_report, name='daily_report'),
    path('chart/',views.chart,name='chart'),
    path('report/chart', views.most_saled_products, name='mosly_saled'),
    path('report/sold', views.most_valued_order, name='important_sold'),
    path('monthly/report/', views.monthly_report, name='monthly_report'),
    path('order/list/', views.order_list, name='order_list'),
    path('order/<int:id>/detail/', views.order_detail, name='order_detail'),
    path('order/<int:id>/pdf/', views.order_pdf, name='order_pdf'),
]