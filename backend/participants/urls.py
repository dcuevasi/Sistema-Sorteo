from django.urls import path
from . import views

app_name = 'participants'

urlpatterns = [
    # Endpoints públicos (participantes)
    path('register/', views.register_participant, name='register'),
    path('verify-email/', views.verify_email, name='verify_email'),
    path('create-password/', views.create_password, name='create_password'),
    path('stats/', views.contest_stats, name='contest_stats'),
    
    # Endpoints de administración
    path('admin/login/', views.admin_login, name='admin_login'),
    path('admin/participants/', views.list_participants, name='list_participants'),
    path('admin/select-winner/', views.select_winner, name='select_winner'),
    path('admin/winners/', views.get_winners, name='get_winners'),
    path('admin/notify-winners/', views.notify_winners, name='notify_winners'),
    path('admin/resend-verification/', views.resend_verification, name='resend_verification'),
]