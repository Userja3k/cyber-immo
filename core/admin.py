from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import *

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'role', 'is_active', 'created_at')
    list_filter = ('role', 'is_active', 'created_at')
    fieldsets = UserAdmin.fieldsets + (
        ('Informations supplémentaires', {
            'fields': ('role', 'phone', 'avatar', 'langue', 'auto_logout')
        }),
    )

@admin.register(Propriete)
class ProprieteAdmin(admin.ModelAdmin):
    list_display = ('titre', 'prix', 'ville', 'status', 'agent', 'created_at')
    list_filter = ('status', 'type_propriete', 'ville', 'created_at')
    search_fields = ('titre', 'description', 'adresse')

@admin.register(ImagePropriete)
class ImageProprieteAdmin(admin.ModelAdmin):
    list_display = ('propriete', 'is_main', 'uploaded_at')
    list_filter = ('is_main', 'uploaded_at')

@admin.register(Vente)
class VenteAdmin(admin.ModelAdmin):
    list_display = ('propriete', 'client_nom', 'prix_vente', 'date_vente', 'vendeur')
    list_filter = ('mode_paiement', 'date_vente')
    search_fields = ('client_nom', 'client_email', 'propriete__titre')

admin.site.register(Ville)
admin.site.register(Quartier)
admin.site.register(TypePropriete)
admin.site.register(StatusPropriete)
admin.site.register(Message)
admin.site.register(UserSettings)