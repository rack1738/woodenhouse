from django.shortcuts import render, redirect
from django.views.generic import *
from .models import *
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.urls import reverse_lazy
from .forms import *
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.db.models import Q
from django.http import JsonResponse


class LoginMixin(object):
    def dispatch(self, request, **kwargs):
        if not request.user.is_authenticated:
            return redirect('woodapp:login')
        return super().dispatch(request, **kwargs)


class ForAllMixin(object):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['productlist'] = Product.objects.order_by('-id')
        context['maincategories'] = ProductCategory.objects.filter(root=None)
        return context


class HomeView(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['productlist'] = Product.objects.order_by('?')
        context['maincategories'] = ProductCategory.objects.filter(root=None)
        return context


class CategoryView(ForAllMixin, TemplateView):
    template_name = 'category.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['productlist'] = Product.objects.order_by('-id')
        context['maincategories'] = ProductCategory.objects.filter(root=None)
        return context


class CategoryDetailView(ForAllMixin, DetailView):
    template_name = 'categorydetail.html'
    model = ProductCategory
    context_object_name = 'categorydetail'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['maincategories'] = ProductCategory.objects.filter(root=None)
        return context


class ProductDetailView(ForAllMixin, DetailView):
    template_name = 'productdetail.html'
    model = Product
    context_object_name = 'productdetail'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['productlist'] = Product.objects.order_by('-id')
        return context


class AddToCartView(View):
    # template_name = 'addtocart.html'

    def get(self, request, **kwargs):
        # context = super().get_context_data(**kwargs)
        if request.is_ajax():
            product = Product.objects.get(id=self.kwargs['pk'])
            cart_id = self.request.session.get('cart_id', None)
            if cart_id:
                cart = Cart.objects.get(id=cart_id)
            else:
                cart = Cart.objects.create(subtotal=0)
                self.request.session['cart_id'] = cart.id

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
            # messages.success(self.request, 'Cart added successfully')
            return JsonResponse({'message': 'Item added successfully'})
        # return redirect('woodapp:productdetail', pk=self.kwargs['pk'])
        # return context


class CartView(ForAllMixin, TemplateView):
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

    def get(self, request, **kwargs):
        if request.is_ajax():
            cart_id = self.request.session.get('cart_id', None)
            cartproduct_id = self.kwargs['cartproduct_id']
            action = self.kwargs['action']
            cart = Cart.objects.get(id=cart_id)
            cartproduct = CartProduct.objects.get(id=cartproduct_id)
            if action == "increase":
                cartproduct.quantity += 1
                cartproduct.subtotal += cartproduct.product.mrp
                cartproduct.save()
                cart.subtotal += cartproduct.product.mrp
                cart.save()
                message = cartproduct.product.title + "'s quantity increased"
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
                message = cartproduct.product.title + "'s quantity decreased"
            elif action == "remove":
                cart.subtotal -= cartproduct.subtotal
                cart.save()
                cartproduct.delete()
                message = cartproduct.product.title + " removed from cart"
            else:
                messages.error(self.request, 'Invalid Operation')

            return JsonResponse({'message': message})
            


class ClearCartView(View):

    def get(self, request):
        cart_id = self.request.session.get('cart_id', None)
        if cart_id:
            cart = Cart.objects.get(id=cart_id)
            cartproducts = cart.cartproduct_set.all()
            if cartproducts:
                cartproducts.delete()
                cart.subtotal = 0
                cart.save()
                messages.success(self.request, 'Cart Cleared successfully')
                return redirect('woodapp:cart')
                context['message'] = "Shopping cart cleared"
            else:
                messages.error(self.request, 'No Items in Cart')
                return redirect('woodapp:cart')

                context['message'] = "no items in cart"
        else:
            messages.error(self.request, 'No Items in Cart')
            return redirect('woodapp:cart')
            context['message'] = "no items in cart"
        


class OrderCreateView(SuccessMessageMixin, CreateView):
    template_name = 'order.html'
    model = Order
    form_class = OrderForm
    success_url = reverse_lazy('woodapp:cart')
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


class LoginView(ForAllMixin, FormView):
    template_name = 'login.html'
    form_class = LoginForm
    success_url = reverse_lazy('woodapp:home')

    def form_valid(self, form):
        u_name = form.cleaned_data['username']
        p_word = form.cleaned_data['password']
        user = authenticate(username=u_name, password=p_word)
        if user is not None:
            login(self.request, user)
        else:
            return render(self.request, self.template_name, {
                'error': "Invalid Username or Password",
                'form': form
            })
        return super().form_valid(form)


class LogoutView(View):
    def get(self, request, **kwargs):
        if request.user.is_authenticated:
            logout(request)
            return redirect('/')


class SignupView(ForAllMixin, FormView):
    template_name = 'signup.html'
    form_class = SignupForm
    success_url = reverse_lazy('woodapp:login')

    def form_valid(self, form):
        u_name = form.cleaned_data['username']
        p_word = form.cleaned_data['password']
        c_pword = form.cleaned_data['confirm_password']
        if p_word != c_pword:
            return render(self.request, self.template_name, {
                'error': "Passwords did not match",
                'form': form
            })
        if User.objects.filter(username=u_name).exists():
            return render(self.request, self.template_name, {
                'error': "User already exists",
                'form': form
            })
        user = User.objects.create_user(username=u_name, password=p_word)
        # user_group = Group.objects.get(name='User')
        # user_group.user_set.add(user)
        # login(self.request, user)
        return super().form_valid(form)


class SearchResultsView(ForAllMixin,TemplateView):
    template_name = 'searchresult.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get('search')
        category = ProductCategory.objects.filter(
            Q(title__icontains=query)
        )
        productlist = Product.objects.filter(
            Q(title__icontains=query) | Q(product_id__icontains=query)
        )
        context['category'] = category
        context['productlist'] = productlist
        return context
