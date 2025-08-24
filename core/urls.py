from django.urls import path
from . import views
urlpatterns = [
    path('products/', views.ProductList.as_view(), name='product-list'),
    path('products/<int:product_id>/', views.ProductDetail.as_view(), name='product-detail'),
    path('interaction/log/', views.LogInteraction.as_view(), name='log-interaction'),
]