from django.db import models
from django.contrib.auth.models import User
import uuid


class Participant(models.Model):
    """
    Participantes del sorteo de San Valentín
    """
    # Verificado?
    PENDING = 'pending'
    VERIFIED = 'verified'
    EXPIRED = 'expired'
    
    STATUS_CHOICES = [
        (PENDING, 'Pendiente'),
        (VERIFIED, 'Verificado'),
        (EXPIRED, 'Expirado'),
    ]

    # Info minima
    full_name = models.CharField(max_length=200)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20)

    # info para verificación
    verification_token = models.UUIDField(default=uuid.uuid4, unique=True)
    verification_status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=PENDING)
    verification_sent_at = models.DateTimeField(null=True, blank=True)
    verified_at = models.DateTimeField(null=True, blank=True)

    # Contraseña (al verificar)
    password = models.CharField(max_length=128, null=True, blank=True)
    
    # Participación
    is_participating = models.BooleanField(default=False)
    
    # Fechas
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.full_name} ({self.email})"

    def can_participate(self):
        return self.verification_status == self.VERIFIED and self.is_participating


class Winner(models.Model):
    """
    Ganadores del sorteo
    """
    participant = models.ForeignKey(Participant, on_delete=models.CASCADE)
    selected_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    draw_date = models.DateTimeField(auto_now_add=True)
    notification_sent = models.BooleanField(default=False)
    notification_sent_at = models.DateTimeField(null=True, blank=True)
    prize_description = models.TextField(default="Estadía de 2 noches para pareja")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-draw_date']

    def __str__(self):
        return f"Ganador: {self.participant.full_name}"
