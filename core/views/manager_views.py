from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.db.models import Count, Sum
from django.utils import timezone
from datetime import datetime, timedelta
from core.models import *
from core.forms import *
import json

def manager_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role not in ['manager', 'admin']:
            messages.error(request, 'Accès non autorisé.')
            return redirect('auth:login')
        return view_func(request, *args, **kwargs)
    return wrapper

@manager_required
def manager_dashboard(request):
    # Statistiques générales
    total_proprietes = Propriete.objects.count()
    total_ventes = Vente.objects.count()
    total_revenus = Vente.objects.aggregate(total=Sum('prix_vente'))['total'] or 0
    
    # Propriétés par statut
    proprietes_par_statut = Propriete.objects.values('status__nom', 'status__couleur').annotate(count=Count('id'))
    
    # Ventes récentes
    ventes_recentes = Vente.objects.select_related('propriete', 'vendeur').order_by('-created_at')[:5]
    
    # Propriétés récentes
    proprietes_recentes = Propriete.objects.select_related('status', 'agent').order_by('-created_at')[:6]
    
    context = {
        'total_proprietes': total_proprietes,
        'total_ventes': total_ventes,
        'total_revenus': total_revenus,
        'proprietes_par_statut': proprietes_par_statut,
        'ventes_recentes': ventes_recentes,
        'proprietes_recentes': proprietes_recentes,
    }
    
    return render(request, 'manager/dashboard.html', context)

@manager_required
def manager_proprietes(request):
    proprietes = Propriete.objects.select_related('status', 'ville', 'agent').order_by('-created_at')
    
    # Filtres
    status_filter = request.GET.get('status')
    ville_filter = request.GET.get('ville')
    
    if status_filter:
        proprietes = proprietes.filter(status_id=status_filter)
    if ville_filter:
        proprietes = proprietes.filter(ville_id=ville_filter)
    
    statuses = StatusPropriete.objects.all()
    villes = Ville.objects.all()
    
    context = {
        'proprietes': proprietes,
        'statuses': statuses,
        'villes': villes,
        'current_status': status_filter,
        'current_ville': ville_filter,
    }
    
    return render(request, 'manager/proprietes.html', context)

@manager_required
def manager_add_propriete(request):
    if request.method == 'POST':
        form = ProprieteForm(request.POST)
        if form.is_valid():
            propriete = form.save(commit=False)
            propriete.agent = request.user
            propriete.save()
            messages.success(request, 'Propriété ajoutée avec succès!')
            return redirect('manager:proprietes')
    else:
        form = ProprieteForm()
    
    return render(request, 'manager/add_propriete.html', {'form': form})

@manager_required
def manager_edit_propriete(request, pk):
    propriete = get_object_or_404(Propriete, pk=pk)
    
    if request.method == 'POST':
        form = ProprieteForm(request.POST, instance=propriete)
        if form.is_valid():
            form.save()
            messages.success(request, 'Propriété modifiée avec succès!')
            return redirect('manager:proprietes')
    else:
        form = ProprieteForm(instance=propriete)
    
    return render(request, 'manager/edit_propriete.html', {'form': form, 'propriete': propriete})

@manager_required
def manager_delete_propriete(request, pk):
    propriete = get_object_or_404(Propriete, pk=pk)
    
    if request.method == 'POST':
        propriete.delete()
        messages.success(request, 'Propriété supprimée avec succès!')
        return redirect('manager:proprietes')
    
    return render(request, 'manager/delete_propriete.html', {'propriete': propriete})

@manager_required
def manager_ventes(request):
    ventes = Vente.objects.select_related('propriete', 'vendeur').order_by('-created_at')
    
    context = {
        'ventes': ventes,
    }
    
    return render(request, 'manager/ventes.html', context)

@manager_required
def manager_add_vente(request):
    if request.method == 'POST':
        form = VenteForm(request.POST)
        if form.is_valid():
            vente = form.save(commit=False)
            vente.vendeur = request.user
            vente.save()
            
            # Mettre à jour le statut de la propriété
            propriete = vente.propriete
            status_vendu = StatusPropriete.objects.get_or_create(nom='Vendu')[0]
            propriete.status = status_vendu
            propriete.save()
            
            messages.success(request, 'Vente enregistrée avec succès!')
            return redirect('manager:ventes')
    else:
        form = VenteForm()
    
    proprietes_disponibles = Propriete.objects.exclude(status__nom='Vendu')
    
    return render(request, 'manager/add_vente.html', {
        'form': form,
        'proprietes_disponibles': proprietes_disponibles
    })

@manager_required
def manager_statistiques(request):
    # Revenus par mois (12 derniers mois)
    end_date = timezone.now()
    start_date = end_date - timedelta(days=365)
    
    ventes_par_mois = []
    for i in range(12):
        month_start = end_date.replace(day=1) - timedelta(days=30*i)
        month_end = month_start.replace(day=28) + timedelta(days=4)
        month_end = month_end - timedelta(days=month_end.day-1) + timedelta(days=31)
        
        revenus = Vente.objects.filter(
            date_vente__gte=month_start,
            date_vente__lt=month_end
        ).aggregate(total=Sum('prix_vente'))['total'] or 0
        
        ventes_par_mois.append({
            'mois': month_start.strftime('%B %Y'),
            'revenus': float(revenus)
        })
    
    ventes_par_mois.reverse()
    
    # Statistiques par statut
    stats_statut = Propriete.objects.values('status__nom', 'status__couleur').annotate(count=Count('id'))
    
    context = {
        'ventes_par_mois': json.dumps(ventes_par_mois),
        'stats_statut': list(stats_statut),
    }
    
    return render(request, 'manager/statistiques.html', context)

@manager_required
def manager_utilisateurs(request):
    utilisateurs = CustomUser.objects.all().order_by('-created_at')
    
    context = {
        'utilisateurs': utilisateurs,
    }
    
    return render(request, 'manager/utilisateurs.html', context)

@manager_required
def manager_feed(request):
    messages_obj = Message.objects.all().order_by('-sent_at')
    
    context = {
        'messages': messages_obj,
    }
    
    return render(request, 'manager/feed.html', context)

@manager_required
def manager_settings(request):
    settings, created = UserSettings.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        theme = request.POST.get('theme')
        langue = request.POST.get('langue')
        auto_logout = request.POST.get('auto_logout')
        
        if theme:
            settings.theme = theme
            settings.save()
        
        if langue:
            request.user.langue = langue
            request.user.save()
        
        if auto_logout:
            request.user.auto_logout = int(auto_logout)
            request.user.save()
        
        messages.success(request, 'Paramètres mis à jour avec succès!')
        return redirect('manager:settings')
    
    context = {
        'settings': settings,
    }
    
    return render(request, 'manager/settings.html', context)

@manager_required
def export_pdf(request):
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
    from io import BytesIO
    
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    
    # En-tête
    p.setFont("Helvetica-Bold", 16)
    p.drawString(100, 750, "Rapport des Propriétés")
    
    # Contenu
    y = 700
    proprietes = Propriete.objects.all()[:20]  # Limiter à 20 pour l'exemple
    
    p.setFont("Helvetica", 10)
    for propriete in proprietes:
        text = f"{propriete.titre} - {propriete.prix}€ - {propriete.status}"
        p.drawString(100, y, text)
        y -= 20
        if y < 100:
            break
    
    p.showPage()
    p.save()
    
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="rapport_proprietes.pdf"'
    
    return response