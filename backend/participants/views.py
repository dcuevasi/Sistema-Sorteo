from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from django.db.models import Q
import random

from .models import Participant, Winner
from .tasks import send_verification_email, send_winner_notification_email
from .serializers import (
    ParticipantRegistrationSerializer,
    EmailVerificationSerializer,
    PasswordCreationSerializer,
    AdminLoginSerializer,
    ParticipantListSerializer,
    WinnerSerializer
)


@api_view(['POST'])
@permission_classes([AllowAny])
def register_participant(request):
    """
    Endpoint para registrar un nuevo participante
    """
    serializer = ParticipantRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        participant = serializer.save()
        
        # Enviar email de verificación con Celery
        send_verification_email.delay(
            participant_email=participant.email,
            participant_name=participant.full_name,
            verification_token=str(participant.verification_token)
        )
        participant.verification_sent_at = timezone.now()
        participant.save()
        
        return Response({
            'message': '¡Gracias por registrarte! Revisa tu correo para verificar tu cuenta.',
            'participant_id': participant.id,
            'verification_token': str(participant.verification_token)  # Solo para desarrollo
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def verify_email(request):
    """
    Endpoint para verificar email con token
    """
    serializer = EmailVerificationSerializer(data=request.data)
    if serializer.is_valid():
        token = serializer.validated_data['token']
        
        try:
            participant = Participant.objects.get(verification_token=token)
            participant.verification_status = Participant.VERIFIED
            participant.verified_at = timezone.now()
            participant.save()
            
            return Response({
                'message': 'Email verificado correctamente. Ahora puedes crear tu contraseña.',
                'token': str(token)
            }, status=status.HTTP_200_OK)
            
        except Participant.DoesNotExist:
            return Response({
                'error': 'Token de verificación inválido.'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def create_password(request):
    """
    Endpoint para crear contraseña después de verificar email
    """
    serializer = PasswordCreationSerializer(data=request.data)
    if serializer.is_valid():
        token = serializer.validated_data['token']
        password = serializer.validated_data['password']
        
        try:
            participant = Participant.objects.get(verification_token=token)
            participant.password = make_password(password)
            participant.is_participating = True
            participant.save()
            
            return Response({
                'message': 'Tu cuenta ha sido activada. ¡Ya estás participando en el sorteo!'
            }, status=status.HTTP_200_OK)
            
        except Participant.DoesNotExist:
            return Response({
                'error': 'Token inválido.'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def admin_login(request):
    """
    Endpoint para login de administradores
    """
    serializer = AdminLoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data['user']
        
        # Generar tokens JWT
        refresh = RefreshToken.for_user(user)
        access = refresh.access_token
        
        return Response({
            'message': 'Login exitoso',
            'access_token': str(access),
            'refresh_token': str(refresh),
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'is_staff': user.is_staff
            }
        }, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_participants(request):
    """
    Endpoint para listar participantes (solo admin)
    """
    if not request.user.is_staff:
        return Response({
            'error': 'No tienes permisos para acceder a esta información.'
        }, status=status.HTTP_403_FORBIDDEN)
    
    # Filtros opcionales
    search = request.query_params.get('search', '')
    status_filter = request.query_params.get('status', '')
    
    participants = Participant.objects.all()
    
    # Aplicar filtros
    if search:
        participants = participants.filter(
            Q(full_name__icontains=search) | 
            Q(email__icontains=search) |
            Q(phone__icontains=search)
        )
    
    if status_filter:
        participants = participants.filter(verification_status=status_filter)
    
    participants = participants.order_by('-created_at')
    
    serializer = ParticipantListSerializer(participants, many=True)
    
    return Response({
        'participants': serializer.data,
        'total': participants.count(),
        'filters': {
            'search': search,
            'status': status_filter
        }
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def select_winner(request):
    """
    Endpoint para seleccionar ganador(es) aleatorio(s)
    """
    if not request.user.is_staff:
        return Response({
            'error': 'No tienes permisos para realizar esta acción.'
        }, status=status.HTTP_403_FORBIDDEN)
    
    # Obtener cantidad de ganadores a seleccionar (default 1)
    count = request.data.get('count', 1)
    if not isinstance(count, int) or count < 1 or count > 10:
        return Response({
            'error': 'La cantidad debe ser un número entre 1 y 10.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Obtener participantes elegibles (no ganadores)
    existing_winners = Winner.objects.values_list('participant_id', flat=True)
    eligible_participants = Participant.objects.filter(
        verification_status=Participant.VERIFIED,
        is_participating=True,
        password__isnull=False
    ).exclude(id__in=existing_winners)
    
    if not eligible_participants.exists():
        return Response({
            'error': 'No hay participantes elegibles para el sorteo.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    if eligible_participants.count() < count:
        return Response({
            'error': f'Solo hay {eligible_participants.count()} participantes elegibles, pero se solicitaron {count} ganadores.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Seleccionar ganadores aleatorios
    selected_participants = random.sample(list(eligible_participants), count)
    
    # Crear registros de ganadores
    winners = []
    winners_data = []
    for participant in selected_participants:
        winner = Winner.objects.create(
            participant=participant,
            selected_by=request.user
        )
        winners.append(winner)
        winners_data.append({
            'id': participant.id,
            'full_name': participant.full_name,
            'email': participant.email,
            'phone': participant.phone,
            'is_winner': True,
            'winner_selected_at': winner.draw_date.isoformat()
        })
    
    return Response({
        'message': f'¡{len(winners)} ganador(es) seleccionado(s)!',
        'winners': winners_data,
        'count': len(winners)
    }, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_winner(request):
    """
    Endpoint para obtener información del ganador actual
    """
    if not request.user.is_staff:
        return Response({
            'error': 'No tienes permisos para acceder a esta información.'
        }, status=status.HTTP_403_FORBIDDEN)
    
    try:
        winner = Winner.objects.latest('draw_date')
        serializer = WinnerSerializer(winner)
        
        return Response({
            'winner': serializer.data
        }, status=status.HTTP_200_OK)
        
    except Winner.DoesNotExist:
        return Response({
            'message': 'Aún no se ha seleccionado ningún ganador.'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([AllowAny])
def contest_stats(request):
    """
    Endpoint público para mostrar estadísticas básicas del concurso
    """
    total_participants = Participant.objects.count()
    verified_participants = Participant.objects.filter(
        verification_status=Participant.VERIFIED
    ).count()
    active_participants = Participant.objects.filter(
        is_participating=True
    ).count()
    
    return Response({
        'total_registered': total_participants,
        'verified': verified_participants,
        'participating': active_participants,
        'winner_selected': Winner.objects.exists()
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_winners(request):
    """
    Endpoint para obtener todos los ganadores seleccionados
    """
    try:
        winners = Winner.objects.select_related('participant').all()
        winners_data = []
        
        for winner in winners:
            winners_data.append({
                'id': winner.participant.id,
                'full_name': winner.participant.full_name,
                'email': winner.participant.email,
                'phone': winner.participant.phone,
                'is_winner': True,
                'winner_selected_at': winner.draw_date.isoformat()
            })
        
        return Response({
            'winners': winners_data,
            'count': len(winners_data)
        }, status=status.HTTP_200_OK)
        
    except Exception:
        return Response({
            'message': 'Error al obtener los ganadores'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def notify_winners(request):
    """
    Endpoint para notificar por email a todos los ganadores
    """
    try:
        winners = Winner.objects.select_related('participant').all()
        
        if not winners.exists():
            return Response({
                'message': 'No hay ganadores para notificar'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Enviar emails a todos los ganadores con Celery
        for winner in winners:
            send_winner_notification_email.delay(
                winner_email=winner.participant.email,
                winner_name=winner.participant.full_name
            )
        
        return Response({
            'message': f'Notificaciones enviadas a {winners.count()} ganador(es)',
            'winners_notified': winners.count()
        }, status=status.HTTP_200_OK)
        
    except Exception:
        return Response({
            'message': 'Error al enviar las notificaciones'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def resend_verification(request):
    """
    Endpoint para reenviar email de verificación a un participante
    """
    email = request.data.get('email')
    
    if not email:
        return Response({
            'message': 'Email es requerido'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        participant = Participant.objects.get(
            email=email,
            verification_status=Participant.PENDING
        )
        
        return Response({
            'message': f'Email de verificación reenviado a {email}'
        }, status=status.HTTP_200_OK)
        
    except Participant.DoesNotExist:
        return Response({
            'message': 'Participante no encontrado o ya verificado'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception:
        return Response({
            'message': 'Error al reenviar la verificación'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
