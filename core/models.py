from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
import uuid

class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Administrateur'),
        ('manager', 'Manager'),
        ('photo_updater', 'Photo Updater'),
    ]
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='photo_updater')
    phone = models.CharField(max_length=20, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    langue = models.CharField(max_length=5, default='fr')
    auto_logout = models.IntegerField(default=30)  # minutes
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

class Ville(models.Model):
    nom = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nom

class Quartier(models.Model):
    nom = models.CharField(max_length=100)
    ville = models.ForeignKey(Ville, on_delete=models.CASCADE, related_name='quartiers')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nom} ({self.ville.nom})"

class TypePropriete(models.Model):
    nom = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return self.nom

class StatusPropriete(models.Model):
    nom = models.CharField(max_length=50)
    couleur = models.CharField(max_length=7, default='#000000')  # Hex color
    
    def __str__(self):
        return self.nom

class Propriete(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    titre = models.CharField(max_length=200)
    description = models.TextField()
    prix = models.DecimalField(max_digits=12, decimal_places=2)
    superficie = models.FloatField()  # en m²
    chambres = models.IntegerField(default=1)
    salles_bain = models.IntegerField(default=1)
    
    # Localisation
    adresse = models.CharField(max_length=300)
    ville = models.ForeignKey(Ville, on_delete=models.CASCADE)
    quartier = models.ForeignKey(Quartier, on_delete=models.CASCADE)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    
    # Relations
    type_propriete = models.ForeignKey(TypePropriete, on_delete=models.CASCADE)
    status = models.ForeignKey(StatusPropriete, on_delete=models.CASCADE)
    agent = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='proprietes')
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.titre
    
    @property
    def image_principale(self):
        image = self.images.filter(is_main=True).first()
        return image.image.url if image else None

class ImagePropriete(models.Model):
    propriete = models.ForeignKey(Propriete, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='proprietes/')
    legende = models.CharField(max_length=200, blank=True)
    is_main = models.BooleanField(default=False)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Image de {self.propriete.titre}"
    
    def save(self, *args, **kwargs):
        # Si cette image est définie comme principale, retirer le flag des autres
        if self.is_main:
            ImagePropriete.objects.filter(propriete=self.propriete, is_main=True).update(is_main=False)
        super().save(*args, **kwargs)

class Vente(models.Model):
    PAYMENT_CHOICES = [
        ('cash', 'Espèces'),
        ('transfer', 'Virement'),
        ('mobile_money', 'Mobile Money'),
        ('credit', 'Crédit'),
    ]
    
    propriete = models.ForeignKey(Propriete, on_delete=models.CASCADE)
    client_nom = models.CharField(max_length=200)
    client_email = models.EmailField()
    client_telephone = models.CharField(max_length=20)
    client_identite = models.CharField(max_length=50)
    client_adresse = models.TextField()
    
    prix_vente = models.DecimalField(max_digits=12, decimal_places=2)
    frais_supplementaires = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    remise = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    mode_paiement = models.CharField(max_length=20, choices=PAYMENT_CHOICES)
    
    date_vente = models.DateTimeField(default=timezone.now)
    vendeur = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Vente de {self.propriete.titre} à {self.client_nom}"
    
    @property
    def total(self):
        return self.prix_vente + self.frais_supplementaires - self.remise

class Message(models.Model):
    from_email = models.EmailField()
    to_email = models.EmailField()
    subject = models.CharField(max_length=200)
    body = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)
    is_feedback = models.BooleanField(default=False)
    is_read = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Message de {self.from_email} - {self.subject}"

class UserSettings(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='settings')
    theme = models.CharField(max_length=10, choices=[('light', 'Clair'), ('dark', 'Sombre')], default='dark')
    notifications_email = models.BooleanField(default=True)
    image_max_width = models.IntegerField(default=1920)
    image_max_height = models.IntegerField(default=1080)
    image_quality = models.IntegerField(default=85)
    
    def __str__(self):
        return f"Paramètres de {self.user.username}"