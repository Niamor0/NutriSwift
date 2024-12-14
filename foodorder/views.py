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
