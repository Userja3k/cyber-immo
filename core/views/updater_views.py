from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from core.models import *
from core.forms import *

def updater_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role not in ['photo_updater', 'admin']:
            messages.error(request, 'Accès non autorisé.')
            return redirect('auth:login')
        return view_func(request, *args, **kwargs)
    return wrapper

@updater_required
def updater_dashboard(request):
    # Propriétés récentes ajoutées par cet utilisateur
    mes_proprietes = Propriete.objects.filter(agent=request.user).order_by('-created_at')[:6]
    
    # Statistiques personnelles
    total_mes_proprietes = Propriete.objects.filter(agent=request.user).count()
    mes_photos = ImagePropriete.objects.filter(propriete__agent=request.user).count()
    
    context = {
        'mes_proprietes': mes_proprietes,
        'total_mes_proprietes': total_mes_proprietes,
        'mes_photos': mes_photos,
    }
    
    return render(request, 'updater/dashboard.html', context)

@updater_required
def updater_proprietes(request):
    proprietes = Propriete.objects.select_related('status', 'ville').order_by('-created_at')
    
    context = {
        'proprietes': proprietes,
    }
    
    return render(request, 'updater/proprietes.html', context)

@updater_required
def updater_photos(request, pk):
    propriete = get_object_or_404(Propriete, pk=pk)
    images = propriete.images.all().order_by('-uploaded_at')
    
    if request.method == 'POST':
        form = ImageProprieteForm(request.POST, request.FILES)
        if form.is_valid():
            image = form.save(commit=False)
            image.propriete = propriete
            image.save()
            messages.success(request, 'Image ajoutée avec succès!')
            return redirect('updater:photos', pk=pk)
    else:
        form = ImageProprieteForm()
    
    context = {
        'propriete': propriete,
        'images': images,
        'form': form,
    }
    
    return render(request, 'updater/photos.html', context)

@updater_required
def updater_add_propriete(request):
    if request.method == 'POST':
        form = ProprieteForm(request.POST)
        if form.is_valid():
            propriete = form.save(commit=False)
            propriete.agent = request.user
            propriete.save()
            messages.success(request, 'Propriété ajoutée avec succès!')
            return redirect('updater:photos', pk=propriete.pk)
    else:
        form = ProprieteForm()
    
    return render(request, 'updater/add_propriete.html', {'form': form})

@updater_required
def updater_carte(request):
    proprietes = Propriete.objects.filter(
        latitude__isnull=False,
        longitude__isnull=False
    ).select_related('status')
    
    # Préparer les données pour la carte
    proprietes_data = []
    for propriete in proprietes:
        proprietes_data.append({
            'id': str(propriete.id),
            'titre': propriete.titre,
            'latitude': propriete.latitude,
            'longitude': propriete.longitude,
            'prix': str(propriete.prix),
            'status': propriete.status.nom,
            'image': propriete.image_principale,
            'couleur': propriete.status.couleur,
        })
    
    context = {
        'proprietes_data': proprietes_data,
    }
    
    return render(request, 'updater/carte.html', context)

@updater_required
def updater_feed(request):
    messages_obj = Message.objects.all().order_by('-sent_at')
    
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.from_email = request.user.email
            message.save()
            messages.success(request, 'Message envoyé avec succès!')
            return redirect('updater:feed')
    else:
        form = MessageForm()
    
    context = {
        'messages': messages_obj,
        'form': form,
    }
    
    return render(request, 'updater/feed.html', context)

@updater_required
def updater_settings(request):
    settings, created = UserSettings.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        theme = request.POST.get('theme')
        image_max_width = request.POST.get('image_max_width')
        image_max_height = request.POST.get('image_max_height')
        image_quality = request.POST.get('image_quality')
        
        if theme:
            settings.theme = theme
            settings.save()
        
        if image_max_width:
            settings.image_max_width = int(image_max_width)
        if image_max_height:
            settings.image_max_height = int(image_max_height)
        if image_quality:
            settings.image_quality = int(image_quality)
        
        settings.save()
        messages.success(request, 'Paramètres mis à jour avec succès!')
        return redirect('updater:settings')
    
    context = {
        'settings': settings,
    }
    
    return render(request, 'updater/settings.html', context)

@csrf_exempt
@updater_required
def upload_photo_ajax(request):
    if request.method == 'POST' and request.FILES.get('image'):
        propriete_id = request.POST.get('propriete_id')
        propriete = get_object_or_404(Propriete, pk=propriete_id)
        
        image = ImagePropriete.objects.create(
            propriete=propriete,
            image=request.FILES['image'],
            legende=request.POST.get('legende', ''),
            is_main=request.POST.get('is_main') == 'true'
        )
        
        return JsonResponse({
            'success': True,
            'image_id': image.id,
            'image_url': image.image.url
        })
    
    return JsonResponse({'success': False})

@csrf_exempt
@updater_required
def delete_photo_ajax(request, photo_id):
    if request.method == 'POST':
        try:
            image = ImagePropriete.objects.get(id=photo_id)
            image.delete()
            return JsonResponse({'success': True})
        except ImagePropriete.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Image non trouvée'})
    
    return JsonResponse({'success': False})