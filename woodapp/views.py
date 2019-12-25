from django.shortcuts import render, redirect
from django.views.generic import *
from .models import *
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages


class HomeView(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['productlist'] = Product.objects.order_by('-id')
        return context


class CategoryView(TemplateView):
    template_name = 'category.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['productlist'] = Product.objects.order_by('-id')
        context['maincategories'] = ProductCategory.objects.filter(root=None)
        return context


class CategoryDetailView(DetailView):
    template_name = 'categorydetail.html'
    model = ProductCategory
    context_object_name = 'categorydetail'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['maincategories'] = ProductCategory.objects.filter(root=None)
        return context


class ProductDetailView(DetailView):
    template_name = 'productdetail.html'
    model = Product
    context_object_name = 'productdetail'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['productlist'] = Product.objects.order_by('-id')
        return context


class AddToCartView(View):
    template_name = 'addtocart.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = Product.objects.get(id=self.kwargs['pk'])
        cart_id = self.request.session.get('cart_id', None)
        if cart_id:
            cart = Cart.objects.get(id=cart_id)
            print("old cart")
        else:
            cart = Cart.objects.create(subtotal=0)
            self.request.session['cart_id'] = cart.id
            print("new cart")

        cartproduct_query = cart.cartproduct_set.filter(product=product)
        if cartproduct_query.exists():
            cartproduct = cartproduct_query.first()
            cartproduct.quantity += 1
            cartproduct.subtotal += product.mrp
            cartproduct.save()
        else:
            cartproduct = CartProduct.objects.create(
                cart=cart, product=product, rate=product.mrp,
                subtotal=product.mrp)
        cart.subtotal += product.mrp
        cart.save()
        messages.success(self.request, 'Cart added successfully')
        return redirect('ecommerceapp:productdetail', pk=self.kwargs['pk'])
        return context


class CartView(TemplateView):
    template_name = 'cart.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart_id = self.request.session.get('cart_id', None)
        if cart_id:
            cart = Cart.objects.get(id=cart_id)
            context['cart'] = cart
            total_qty = 0
            for cp in cart.cartproduct_set.all():
                total_qty += cp.quantity
            context['total_qty'] = total_qty
        return context


class ManageCartView(View):
    template_name = 'managecart.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        cart_id = self.request.session.get('cart_id', None)
        cartproduct_id = self.kwargs['cartproduct_id']
        action = self.kwargs['action']
        cart = Cart.objects.get(id=cart_id)
        cartproduct = CartProduct.objects.get(id=cartproduct_id)
        # extras = request.GET.get('extras')
        # print(extras)
        if action == "increase":
            cartproduct.quantity += 1
            cartproduct.subtotal += cartproduct.product.mrp
            cartproduct.save()
            cart.subtotal += cartproduct.product.mrp
            cart.save()
            messages.success(
                self.request, cartproduct.product.title + "'s quantity increased")
            context['message'] = "Item quantity increased"
        elif action == "decrease":
            cartproduct.quantity -= 1
            cartproduct.subtotal -= cartproduct.product.mrp
            if cartproduct.quantity <= 0:
                cartproduct.delete()
                cart.subtotal = 0
            else:
                cartproduct.save()
                cart.subtotal -= cartproduct.product.mrp
            cart.save()
            messages.success(
                self.request, cartproduct.product.title + "'s quantity decreased")
            context['message'] = "Item quantity decreased"
        elif action == "remove":
            cart.subtotal -= cartproduct.subtotal
            cart.save()
            cartproduct.delete()
            messages.success(
                self.request, cartproduct.product.title + " removed from cart")

            context['message'] = "Item removed from cart"
        else:
            messages.error(self.request, 'Invalid Operation')
            context['message'] = "Invalid Operation"
        return redirect('ecommerceapp:cart')
    return context


class ClearCartView(View):
    template_name = 'managecart.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart_id = self.request.session.get('cart_id', None)
        if cart_id:
            cart = Cart.objects.get(id=cart_id)
            cartproducts = cart.cartproduct_set.all()
            if cartproducts:
                cartproducts.delete()
                cart.subtotal = 0
                cart.save()
                messages.success(self.request, 'Cart Cleared successfully')
                return redirect('ecommerceapp:cart')
                context['message'] = "Shopping cart cleared"
            else:
                messages.error(self.request, 'No Items in Cart')
                return redirect('ecommerceapp:cart')

                context['message'] = "no items in cart"
        else:
            messages.error(self.request, 'No Items in Cart')
            return redirect('ecommerceapp:cart')
            context['message'] = "no items in cart"
        return context


class OrderCreateView(SuccessMessageMixin, CreateView):
    template_name = 'order.html'
    model = Order
    form_class = OrderForm
    success_url = reverse_lazy('ecommerceapp:home')
    success_message = 'Order placed successfully'

    def form_valid(self, form):
        cart_id = self.request.session.get('cart_id', None)
        if cart_id:
            cart = Cart.objects.get(id=cart_id)
            form.instance.cart = cart
            form.instance.subtotal = cart.subtotal
            form.instance.discount = 0
            form.instance.total = form.instance.subtotal - form.instance.discount
            self.request.session['cart_id'] = None
        return super().form_valid(form)
