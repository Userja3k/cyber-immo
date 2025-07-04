from rest_framework import serializers
from .models import *

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    
    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'role', 'password')
    
    def create(self, validated_data):
        password = validated_data.pop('password')
        user = CustomUser.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user

class ImageProprieteSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImagePropriete
        fields = '__all__'

class ProprieteSerializer(serializers.ModelSerializer):
    images = ImageProprieteSerializer(many=True, read_only=True)
    agent_name = serializers.CharField(source='agent.username', read_only=True)
    status_name = serializers.CharField(source='status.nom', read_only=True)
    ville_name = serializers.CharField(source='ville.nom', read_only=True)
    
    class Meta:
        model = Propriete
        fields = '__all__'

class VenteSerializer(serializers.ModelSerializer):
    propriete_titre = serializers.CharField(source='propriete.titre', read_only=True)
    vendeur_name = serializers.CharField(source='vendeur.username', read_only=True)
    
    class Meta:
        model = Vente
        fields = '__all__'

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = '__all__'