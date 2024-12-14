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
