from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import *

class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'cyber-input',
        'placeholder': 'Nom d\'utilisateur ou email'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'cyber-input',
        'placeholder': 'Mot de passe'
    }))

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    role = forms.ChoiceField(choices=CustomUser.ROLE_CHOICES)
    
    class Meta:
        model = CustomUser
        fields = ("username", "email", "first_name", "last_name", "role", "password1", "password2")

class ProprieteForm(forms.ModelForm):
    class Meta:
        model = Propriete
        exclude = ['agent', 'created_at', 'updated_at']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'latitude': forms.HiddenInput(),
            'longitude': forms.HiddenInput(),
        }

class ImageProprieteForm(forms.ModelForm):
    class Meta:
        model = ImagePropriete
        fields = ['image', 'legende', 'is_main']

class VenteForm(forms.ModelForm):
    class Meta:
        model = Vente
        exclude = ['vendeur', 'created_at']
        widgets = {
            'date_vente': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'client_adresse': forms.Textarea(attrs={'rows': 3}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['to_email', 'subject', 'body']
        widgets = {
            'body': forms.Textarea(attrs={'rows': 6}),
        }