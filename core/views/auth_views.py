from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from core.forms import CustomAuthenticationForm, CustomUserCreationForm
from core.models import CustomUser

def login_view(request):
    if request.user.is_authenticated:
        # Rediriger selon le rôle
        if request.user.role == 'manager':
            return redirect('manager:dashboard')
        elif request.user.role == 'photo_updater':
            return redirect('updater:dashboard')
        elif request.user.role == 'admin':
            return redirect('auth:admin_portal')
    
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            
            if user is not None:
                login(request, user)
                messages.success(request, f'Bienvenue {user.first_name or user.username} !')
                
                # Redirection selon le rôle
                if user.role == 'manager':
                    return redirect('manager:dashboard')
                elif user.role == 'photo_updater':
                    return redirect('updater:dashboard')
                elif user.role == 'admin':
                    return redirect('auth:admin_portal')
            else:
                messages.error(request, 'Identifiants invalides.')
    else:
        form = CustomAuthenticationForm()
    
    return render(request, 'auth/login.html', {'form': form})

def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Compte créé avec succès ! Vous pouvez maintenant vous connecter.')
            return redirect('auth:login')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'auth/register.html', {'form': form})

def forgot_password_view(request):
    return render(request, 'auth/forgot_password.html')

@login_required
def admin_portal_view(request):
    if request.user.role != 'admin':
        messages.error(request, 'Accès non autorisé.')
        return redirect('auth:login')
    
    return render(request, 'auth/admin_portal.html')

def logout_view(request):
    logout(request)
    messages.success(request, 'Vous avez été déconnecté avec succès.')
    return redirect('auth:login')