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
    path('cart/', CartView.as_view(), name='cart'),
    path('clear-cart/', ClearCartView.as_view(), name='clearcart'),
    path('manage-cart/<cartproduct_id>/<action>/',
         ManageCartView.as_view(), name='managecart'),

    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('signup/', SignupView.as_view(), name='signup'),
    path('search/', SearchResultsView.as_view(), name='search_results'),

    path('order/', OrderCreateView.as_view(), name='order'),
    
]
