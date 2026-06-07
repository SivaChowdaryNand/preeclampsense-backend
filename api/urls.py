"""
API URL routes for PreeclampSense.
"""
from django.urls import path
from . import views

urlpatterns = [
    path('sync/bp/', views.sync_bp, name='sync-bp'),
    path('sync/urine/', views.sync_urine, name='sync-urine'),
    path('alerts/', views.create_alert, name='create-alert'),
    path('alerts/<int:alert_id>/resolve/', views.resolve_alert, name='resolve-alert'),
    path('dashboard/', views.dashboard_stats, name='dashboard'),
]
