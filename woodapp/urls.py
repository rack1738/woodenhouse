from django.urls import path
from .views import *


app_name = 'woodapp'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('category/', CategoryView.as_view(), name='category'),
    path('category/<int:pk>/detail/',
         CategoryDetailView.as_view(), name='categorydetail'),
    path('product/<int:pk>/detail/',
         ProductDetailView.as_view(), name='productdetail'),
    path('product/<int:pk>/add-to-cart/',
         AddToCartView.as_view(), name='addtocart'),

]
