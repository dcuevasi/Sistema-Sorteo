from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import logging

logger = logging.getLogger(__name__)

@shared_task
def send_verification_email(participant_email, participant_name, verification_token):
    """
    Envía email de verificación de forma asíncrona
    """
    try:
        # URL de verificación
        verification_url = f"http://localhost:5173/verify-email?token={verification_token}"
        
        subject = 'Verifica tu email - Sorteo San Valentín'
        
        # Mensaje en formato HTML
        html_message = f"""
        <html>
            <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; text-align: center; color: white;">
                    <h1 style="margin: 0;">Sorteo San Valentín</h1>
                    <p style="margin: 10px 0 0 0; font-size: 18px;">¡Una estadía romántica te espera!</p>
                </div>
                
                <div style="padding: 30px; background: #f9f9f9;">
                    <h2 style="color: #333;">¡Hola {participant_name}!</h2>
                    
                    <p style="font-size: 16px; line-height: 1.6; color: #666;">
                        ¡Gracias por registrarte en nuestro sorteo de San Valentín!
                    </p>
                    
                    <p style="font-size: 16px; line-height: 1.6; color: #666;">
                        Para completar tu registro y participar por <strong>una estadía de 2 noches 
                        todo pagado para una pareja</strong>, necesitas verificar tu email haciendo clic 
                        en el botón de abajo:
                    </p>
                    
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="{verification_url}" 
                           style="background: linear-gradient(45deg, #667eea, #764ba2); 
                                  color: white; 
                                  padding: 15px 30px; 
                                  text-decoration: none; 
                                  border-radius: 8px; 
                                  font-weight: bold;
                                  display: inline-block;">
                              Verificar mi Email
                        </a>
                    </div>
                    
                    <p style="font-size: 14px; color: #888;">
                        Si no puedes hacer clic en el botón, copia y pega esta URL en tu navegador:<br>
                        <a href="{verification_url}" style="color: #667eea;">{verification_url}</a>
                    </p>
                    
                    <p style="font-size: 14px; color: #888; margin-top: 30px;">
                        Este enlace expirará en 24 horas. Si no fuiste tú quien se registró, 
                        puedes ignorar este email.
                    </p>
                </div>
                
                <div style="background: #333; color: white; padding: 20px; text-align: center;">
                    <p style="margin: 0; font-size: 14px;">
                        CTS Turismo - Sorteo San Valentín 2025
                    </p>
                </div>
            </body>
        </html>
        """
        
        # Mensaje de texto en plano
        text_message = f"""
        ¡Hola {participant_name}!
        
        ¡Gracias por registrarte en nuestro sorteo de San Valentín! 
        
        Para completar tu registro y participar por una estadía de 2 noches 
        todo pagado para una pareja, necesitas verificar tu email.
        
        Haz clic en este enlace para verificar:
        {verification_url}
        
        Este enlace expirará en 24 horas.
        
        ¡Buena suerte!
        CTS Turismo
        """
        
        send_mail(
            subject=subject,
            message=text_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[participant_email],
            html_message=html_message,
            fail_silently=False
        )
        
        logger.info(f"Email de verificación enviado a {participant_email}")
        return f"Email enviado exitosamente a {participant_email}"
        
    except Exception as e:
        logger.error(f"Error enviando email de verificación a {participant_email}: {str(e)}")
        raise


@shared_task
def send_winner_notification_email(winner_email, winner_name):
    """
    Envía email de notificación al ganador de forma asíncrona
    """
    try:
        subject = ' ¡FELICIDADES! Ganaste el Sorteo San Valentín'
        
        # Mensaje HTML
        html_message = f"""
        <html>
            <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <div style="background: linear-gradient(135deg, #f39c12 0%, #e74c3c 100%); padding: 30px; text-align: center; color: white;">
                    <h1 style="margin: 0; font-size: 32px;"> ¡GANASTE!</h1>
                    <p style="margin: 10px 0 0 0; font-size: 20px;">Sorteo San Valentín 2025</p>
                </div>
                
                <div style="padding: 30px; background: #fff;">
                    <h2 style="color: #e74c3c; text-align: center;">¡Felicidades {winner_name}!</h2>
                    
                    <div style="background: #fff3e0; border-left: 4px solid #f39c12; padding: 20px; margin: 20px 0;">
                        <h3 style="color: #f39c12; margin-top: 0;"> Tu Premio:</h3>
                        <p style="font-size: 18px; color: #333; margin-bottom: 0;">
                            <strong>Una estadía romántica de 2 noches todo pagado para una pareja</strong>
                        </p>
                    </div>
                    
                    <p style="font-size: 16px; line-height: 1.6; color: #666;">
                        Has sido seleccionado como el <strong>ganador oficial</strong> de nuestro 
                        sorteo de San Valentín. ¡Prepárate para vivir una experiencia inolvidable! 
                    </p>
                    
                    <h3 style="color: #333;"> Próximos pasos:</h3>
                    <ol style="color: #666; line-height: 1.8;">
                        <li><strong>Te contactaremos</strong> en las próximas 48 horas</li>
                        <li><strong>Validaremos tu identidad</strong> y eligibilidad</li>
                        <li><strong>Coordinaremos</strong> las fechas disponibles</li>
                        <li><strong>¡Disfruta</strong> tu estadía romántica!</li>
                    </ol>
                    
                    <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0;">
                        <p style="margin: 0; font-size: 14px; color: #666;">
                            <strong>Importante:</strong> Guarda este email como comprobante. 
                            Solo contactaremos a través de nuestros canales oficiales de CTS Turismo.
                        </p>
                    </div>
                </div>
                
                <div style="background: #333; color: white; padding: 20px; text-align: center;">
                    <p style="margin: 0; font-size: 14px;">
                        CTS Turismo - Sorteo San Valentín 2025<br>
                        ¡Gracias por participar! 
                    </p>
                </div>
            </body>
        </html>
        """
        
        # Mensaje de texto plano
        text_message = f"""
        ¡FELICIDADES {winner_name}!
        
        HAS GANADO EL SORTEO SAN VALENTÍN 2025
        
        Tu premio: Una estadía romántica de 2 noches todo pagado para una pareja
        
        Próximos pasos:
        1. Te contactaremos en las próximas 48 horas
        2. Validaremos tu identidad y eligibilidad  
        3. Coordinaremos las fechas disponibles
        4. ¡Disfruta tu estadía romántica!
        
        Guarda este email como comprobante.
        
        ¡Felicidades nuevamente!
        CTS Turismo
        """
        
        send_mail(
            subject=subject,
            message=text_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[winner_email],
            html_message=html_message,
            fail_silently=False
        )
        
        logger.info(f"Email de ganador enviado a {winner_email}")
        return f"Email de ganador enviado exitosamente a {winner_email}"
        
    except Exception as e:
        logger.error(f"Error enviando email de ganador a {winner_email}: {str(e)}")
        raise