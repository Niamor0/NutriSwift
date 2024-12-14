from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import *
from django.db.models import Count, Sum, F, Q
from decimal import Decimal
from django.utils import timezone
from django.http import JsonResponse, Http404


def Home(request):
    return render(request, 'home.html')

def is_admin(user):
    return user.is_staff
def user_signup(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        phone = request.POST.get('phone')
        address = request.POST.get('address')

        # Validation
        if password != confirm_password:
            messages.error(request, 'Passwords do not match!')
            return redirect('signup')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists!')
            return redirect('signup')

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered!')
            return redirect('signup')

        try:
            # Create User
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password
            )

            # Create UserProfile
            UserProfile.objects.create(
                user=user,
                phone=phone,
                address=address
            )

            messages.success(request, 'Account created successfully! Please login.')
            return redirect('login')

        except Exception as e:
            messages.error(request, f'Error creating account: {str(e)}')
            return redirect('signup')

    return render(request, 'signup.html')
def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            if user.is_staff:
                messages.error(request, 'Please use admin login page!')
                return redirect('admin_login')
            
            login(request, user)
            messages.success(request, f'Welcome back, {username}!')
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password!')
            return redirect('login')

    return render(request, 'login.html')
def admin_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None and user.is_staff:
            login(request, user)
            messages.success(request, f'Welcome back, Admin {username}!')
            return redirect('admin_dashboard')
        else:
            messages.error(request, 'Invalid admin credentials!')
            return redirect('admin_login')

    return render(request, 'admin_login.html')

@login_required
def user_logout(request):
    logout(request)
    messages.success(request, 'Logged out successfully!')
    return redirect('home')

@login_required
def user_profile(request):
    user = request.user
    profile = user.userprofile
    return render(request, 'profile.html', {'user': user, 'profile': profile})


@login_required(login_url='login')
@user_passes_test(is_admin)
def admin_dashboard(request):
    # Basic stats
    total_users = User.objects.filter(is_staff=False).count()
    total_orders = Order.objects.count()
    recent_orders = Order.objects.order_by('-created_at')[:5]

    # Calculate total revenue
    total_revenue = Order.objects.filter(
        status='Delivered'
    ).aggregate(
        total=Sum('total_price')
    )['total'] or 0

    # Count products by category
    product_counts = {
        'Pizza': Pizza.objects.count(),
        'Pasta': Pasta.objects.count(),
        'Burger': Burger.objects.count(),
        'Dessert': Dessert.objects.count(),
    }

    # Orders by status
    orders_by_status = Order.objects.values('status').annotate(
        count=Count('id')
    )

    context = {
        'total_users': total_users,
        'total_orders': total_orders,
        'total_revenue': total_revenue,
        'recent_orders': recent_orders,
        'product_counts': product_counts,
        'orders_by_status': orders_by_status,
    }

    return render(request, 'admin/dashboard.html', context)


@login_required
@user_passes_test(is_admin)
def admin_orders(request):
    orders = Order.objects.all().order_by('-created_at')
    return render(request, 'admin/orders.html', {'orders': orders})

@login_required
@user_passes_test(is_admin)
def admin_users(request):
    users = User.objects.filter(is_staff=False).order_by('-date_joined')
    return render(request, 'admin/users.html', {'users': users})

@login_required
@user_passes_test(is_admin)
def admin_order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'admin/order_detail.html', {'order': order})

@login_required
@user_passes_test(is_admin)
def update_order_status(request, order_id):
    if request.method == 'POST':
        order = get_object_or_404(Order, id=order_id)
        new_status = request.POST.get('status')
        if new_status in [choice[0] for choice in Order.STATUS_CHOICES]:
            order.status = new_status
            order.save()
            messages.success(request, f'Order #{order_id} status updated to {new_status}')
        else:
            messages.error(request, 'Invalid status!')
    return redirect('admin_order_detail', order_id=order_id)

@login_required
@user_passes_test(is_admin)
def add_product(request, product_type):
    product_models = {
        'pizza': Pizza,
        'pasta': Pasta,
        'burger': Burger,
        'dessert': Dessert
    }
    
    model = product_models.get(product_type.lower())
    if not model:
        raise Http404("Product type does not exist")
    
    if request.method == 'POST':
        name = request.POST.get('name')
        price = request.POST.get('price')
        image = request.FILES.get('image')
        
        try:
            model.objects.create(
                name=name,
                price=price,
                image=image
            )
            messages.success(request, f'{product_type.capitalize()} added successfully!')
        except Exception as e:
            messages.error(request, f'Error adding {product_type.capitalize()}: {str(e)}')
    
    return redirect('admin_dashboard')



@login_required
@user_passes_test(is_admin)
def update_product(request, product_type, product_id):
    product_models = {
        'pizza': Pizza,
        'pasta': Pasta,
        'burger': Burger,
        'dessert': Dessert
    }
    
    model = product_models.get(product_type.lower())
    if not model:
        raise Http404("Product type does not exist")
    
    product = get_object_or_404(model, id=product_id)
    
    if request.method == 'POST':
        name = request.POST.get('name')
        price = request.POST.get('price')
        image = request.FILES.get('image')
        
        try:
            product.name = name
            product.price = price
            if image:
                product.image = image
            product.save()
            messages.success(request, f'{product_type.capitalize()} updated successfully!')
        except Exception as e:
            messages.error(request, f'Error updating {product_type.capitalize()}: {str(e)}')
    
    return redirect('admin_dashboard')

@login_required
@user_passes_test(is_admin)
def delete_product(request, product_type, product_id):
    product_models = {
        'pizza': Pizza,
        'pasta': Pasta,
        'burger': Burger,
        'dessert': Dessert
    }
    
    model = product_models.get(product_type.lower())
    if not model:
        raise Http404("Product type does not exist")
    
    product = get_object_or_404(model, id=product_id)
    product.delete()
    
    messages.success(request, f'{product_type.capitalize()} deleted successfully!')
    return redirect('admin_dashboard')

@login_required
@user_passes_test(is_admin)
def delivery_management(request):
    deliveries = Delivery.objects.all().order_by('-id')
    if request.method == 'POST':
        delivery_id = request.POST.get('delivery_id')
        new_status = request.POST.get('delivery_status')
        delivery = get_object_or_404(Delivery, id=delivery_id)
        if new_status in dict(Delivery.DELIVERY_STATUS_CHOICES):
            delivery.delivery_status = new_status
            delivery.save()
            messages.success(request, f"Delivery status updated to {new_status}.")
        else:
            messages.error(request, "Invalid delivery status.")
    return render(request, 'admin/deliveries.html', {'deliveries': deliveries})

@login_required
@user_passes_test(is_admin)
def order_management(request):
    orders = Order.objects.all().order_by('-created_at')
    return render(request, 'admin/orders.html', {'orders': orders})


@login_required
@user_passes_test(is_admin)
def admin_logout(request):
    logout(request)
    messages.success(request, 'Logged out successfully!')
    return redirect('home')



def PizzaView(request):
    pizzas = Pizza.objects.all()
    return render(request, 'pizza.html', {'pizzas': pizzas})

def PastaView(request):
    pastas = Pasta.objects.all()
    return render(request, 'pasta.html', {'pastas': pastas})

def BurgerView(request):
    burgers = Burger.objects.all()
    return render(request, 'burger.html', {'burgers': burgers})

def DessertView(request):
    desserts = Dessert.objects.all()
    return render(request, 'dessert.html', {'desserts': desserts})

def product_detail(request, product_type, product_id):
    # Map product types to models
    product_models = {
        'pizza': Pizza,
        'pasta': Pasta,
        'burger': Burger,
        'dessert': Dessert
    }
    
    # Get the appropriate model
    model = product_models.get(product_type.lower())
    if not model:
        raise Http404("Product type does not exist")
    
    # Get the product
    product = get_object_or_404(model, id=product_id)
    
    context = {
        'product': product,
        'product_type': product_type.lower()  # Pass this to template for cart URL
    }
    
    return render(request, 'product_detail.html', context)
