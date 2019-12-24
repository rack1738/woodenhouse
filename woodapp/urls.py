from django.urls import path
from .views import *


app_name = 'woodapp'

urlpatterns =[
	path('',HomeView.as_view(), name='home'),


]