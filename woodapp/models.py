from django.db import models
from django.contrib.auth.models import User


class EcommAdmin(models.Model):
	user = models.OneToOneField(User, on_delete = models.CASCADE)
	mobile = models.CharField(max_length=30, null=True, blank=True)

	def __str__(self):
		return self.user.username	


class Customer(models.Model):
	user = models.OneToOneField(User, on_delete = models.CASCADE)
	mobile = models.CharField(max_length=30, null=True, blank=True)

	def __str__(self):
		return self.user.username


class ProductCategory(models.Model):
	title = models.CharField(max_length=200)
	slug = models.SlugField(null=True, blank=True, unique=True)
	root = models.ForeignKey(
		'self', on_delete=models.SET_NULL, null=True, blank=True)

	def __str__(self):
		return self.title


class Product(models.Model):
	title = models.CharField(max_length=200)
	category = models.ForeignKey(
		ProductCategory, on_delete=models.CASCADE, related_name='products')
	product_id = models.CharField(max_length=200, unique=True)
	mrp = models.DecimalField(max_digits=10, decimal_places=2)
	image = models.ImageField(upload_to="product")

	def __str__(self):
		return self.title


class Cart(models.Model):
	customer = models.ForeignKey(
		Customer, on_delete=models.SET_NULL, null=True, blank=True)
	subtotal = models.DecimalField(max_digits=10, decimal_places=2)

	def __str__(self):
		return "Cart Id: #" + str(self.id)


class CartProduct(models.Model):
	cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
	product = models.ForeignKey(Product, on_delete=models.CASCADE)
	rate = models.DecimalField(max_digits=10, decimal_places=2)
	quantity = models.PositiveIntegerField(default=1)
	subtotal = models.DecimalField(max_digits=10, decimal_places=2)

	def __str__(self):
		return self.product.title


class Order(models.Model):
	cart = models.OneToOneField(Cart, on_delete=models.CASCADE)
	subtotal = models.DecimalField(max_digits=10, decimal_places=2)
	discount = models.DecimalField(max_digits=10, decimal_places=2)
	total = models.DecimalField(max_digits=10, decimal_places=2)
	city = models.CharField(max_length=200)
	street = models.CharField(max_length=200)
	mobile = models.CharField(max_length=15)
	delivery_date = models.DateField(null=True, blank=True)
	ordered_date = models.DateField(auto_now_add=True)

	
	def __str__(self):
		return "Order Id: #" + str(self.id)