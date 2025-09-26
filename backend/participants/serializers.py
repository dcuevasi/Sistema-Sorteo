from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from .models import Participant, Winner
import uuid


class ParticipantRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer para el registro inicial de participantes
    """
    class Meta:
        model = Participant
        fields = ['full_name', 'email', 'phone']
        
    def validate_email(self, value):
        """
        Validar que el email no esté ya registrado
        """
        if Participant.objects.filter(email=value).exists():
            raise serializers.ValidationError("Este correo ya está registrado en el concurso.")
        return value

    def create(self, validated_data):
        """
        Crear participante con token de verificación
        """
        participant = Participant.objects.create(
            full_name=validated_data['full_name'],
            email=validated_data['email'],
            phone=validated_data['phone'],
            verification_token=uuid.uuid4()
        )
        return participant


class EmailVerificationSerializer(serializers.Serializer):
    """
    Serializer para verificar email con token
    """
    token = serializers.UUIDField()

    def validate_token(self, value):
        """
        Validar que el token existe y no ha expirado
        """
        try:
            participant = Participant.objects.get(verification_token=value)
            if participant.verification_status == Participant.VERIFIED:
                raise serializers.ValidationError("Este email ya ha sido verificado.")
            if participant.verification_status == Participant.EXPIRED:
                raise serializers.ValidationError("El token de verificación ha expirado.")
        except Participant.DoesNotExist:
            raise serializers.ValidationError("Token de verificación inválido.")
        
        return value


class PasswordCreationSerializer(serializers.Serializer):
    """
    Serializer para crear contraseña después de verificar email
    """
    token = serializers.UUIDField()
    password = serializers.CharField(min_length=8, max_length=128)
    password_confirm = serializers.CharField(min_length=8, max_length=128)

    def validate(self, data):
        """
        Validar que las contraseñas coincidan
        """
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError("Las contraseñas no coinciden.")
        return data

    def validate_token(self, value):
        """
        Validar que el token existe y el email está verificado
        """
        try:
            participant = Participant.objects.get(verification_token=value)
            if participant.verification_status != Participant.VERIFIED:
                raise serializers.ValidationError("Primero debes verificar tu email.")
            if participant.password:
                raise serializers.ValidationError("Ya has creado tu contraseña.")
        except Participant.DoesNotExist:
            raise serializers.ValidationError("Token inválido.")
        
        return value


class AdminLoginSerializer(serializers.Serializer):
    """
    Serializer para login de administradores
    """
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        """
        Validar credenciales de admin
        """
        username = data.get('username')
        password = data.get('password')

        if username and password:
            user = authenticate(username=username, password=password)
            if user:
                if user.is_active and user.is_staff:
                    data['user'] = user
                    return data
                else:
                    raise serializers.ValidationError("Este usuario no tiene permisos de administrador.")
            else:
                raise serializers.ValidationError("Credenciales inválidas.")
        else:
            raise serializers.ValidationError("Debes proporcionar usuario y contraseña.")


class ParticipantListSerializer(serializers.ModelSerializer):
    """
    Serializer para listar participantes (panel admin)
    """
    can_participate = serializers.ReadOnlyField()
    
    class Meta:
        model = Participant
        fields = [
            'id', 'full_name', 'email', 'phone', 
            'verification_status', 'is_participating', 
            'verified_at', 'created_at', 'can_participate'
        ]


class WinnerSelectionSerializer(serializers.Serializer):
    """
    Serializer para seleccionar ganador aleatorio
    """
    selected_by_id = serializers.IntegerField()

    def validate_selected_by_id(self, value):
        """
        Validar que el usuario existe y es admin
        """
        try:
            user = User.objects.get(id=value)
            if not user.is_staff:
                raise serializers.ValidationError("Solo administradores pueden seleccionar ganadores.")
        except User.DoesNotExist:
            raise serializers.ValidationError("Usuario no encontrado.")
        
        return value


class WinnerSerializer(serializers.ModelSerializer):
    """
    Serializer para mostrar información del ganador
    """
    participant_name = serializers.CharField(source='participant.full_name', read_only=True)
    participant_email = serializers.CharField(source='participant.email', read_only=True)
    selected_by_username = serializers.CharField(source='selected_by.username', read_only=True)
    
    class Meta:
        model = Winner
        fields = [
            'id', 'participant_name', 'participant_email', 
            'selected_by_username', 'draw_date', 'notification_sent',
            'notification_sent_at', 'prize_description'
        ]