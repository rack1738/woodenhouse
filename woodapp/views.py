from django.shortcuts import render
from django.views.generic import *
from .models import *


class HomeView(TemplateView):
	template_name = 'home.html'

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['productlist'] = Product.objects.order_by('-id')
		return context

