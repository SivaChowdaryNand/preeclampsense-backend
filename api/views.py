# backend/api/serializers.py
from rest_framework import serializers
from preeclampsense.models import Patient, BPMeasurement, UrineTest, AlertLog


class BPMeasurementSerializer(serializers.ModelSerializer):
    class Meta:
        model  = BPMeasurement
        fields = '__all__'


class UrineTestSerializer(serializers.ModelSerializer):
    protein_label = serializers.ReadOnlyField()

    class Meta:
        model  = UrineTest
        fields = '__all__'


class AlertLogSerializer(serializers.ModelSerializer):
    class Meta:
        model  = AlertLog
        fields = '__all__'


class PatientSerializer(serializers.ModelSerializer):
    bp_measurements = BPMeasurementSerializer(many=True, read_only=True)
    urine_tests     = UrineTestSerializer(many=True, read_only=True)

    class Meta:
        model  = Patient
        fields = '__all__'


# ─── Views ────────────────────────────────────────────────────────────────────
# backend/api/views.py
from rest_framework.decorators import api_view
from rest_framework.response   import Response
from rest_framework            import status
from django.utils              import timezone
from datetime                  import timedelta
from preeclampsense.models     import Patient, BPMeasurement, UrineTest, AlertLog


@api_view(['POST'])
def sync_bp(request):
    """
    POST /api/sync/bp/
    Body: { patient_phone, systolic, diastolic, heart_rate, spo2, risk_score, risk_level, timestamp }
    """
    d = request.data
    try:
        patient, _ = Patient.objects.get_or_create(
            phone=d['patient_phone'],
            defaults={
                'name':             d.get('name', 'Unknown'),
                'age':              d.get('age', 25),
                'gestational_week': d.get('gestational_week', 24),
                'village':          d.get('village', ''),
            }
        )
        BPMeasurement.objects.create(
            patient     = patient,
            systolic    = d['systolic'],
            diastolic   = d['diastolic'],
            heart_rate  = d.get('heart_rate', 72),
            spo2        = d.get('spo2', 98),
            risk_score  = d.get('risk_score', 0),
            risk_level  = d.get('risk_level', 'normal'),
        )
        return Response({'status': 'ok'})
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def sync_urine(request):
    """
    POST /api/sync/urine/
    Body: { patient_phone, protein_class, confidence, trigger_systolic, trigger_diastolic }
    """
    d = request.data
    try:
        patient = Patient.objects.get(phone=d['patient_phone'])
        UrineTest.objects.create(
            patient           = patient,
            protein_class     = d['protein_class'],
            confidence        = d['confidence'],
            trigger_systolic  = d['trigger_systolic'],
            trigger_diastolic = d['trigger_diastolic'],
        )
        return Response({'status': 'ok'})
    except Patient.DoesNotExist:
        return Response({'error': 'Patient not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def create_alert(request):
    """
    POST /api/alerts/
    Called by app when danger level is detected.
    """
    d = request.data
    try:
        alert = AlertLog.objects.create(
            patient_name     = d.get('patient_name', 'Unknown'),
            village          = d.get('village', ''),
            gestational_week = d.get('gestational_week', 0),
            systolic         = d.get('systolic', 0),
            diastolic        = d.get('diastolic', 0),
            protein_class    = d.get('protein_class', 0),
            maps_url         = d.get('maps_url', ''),
        )
        return Response({'status': 'ok', 'alert_id': alert.id})
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def dashboard_stats(request):
    """
    GET /api/dashboard/
    Returns summary stats for doctor dashboard.
    """
    last_24h = timezone.now() - timedelta(hours=24)
    last_7d  = timezone.now() - timedelta(days=7)

    total_patients      = Patient.objects.count()
    high_bp_today       = BPMeasurement.objects.filter(
        timestamp__gte=last_24h
    ).filter(
        systolic__gte=140
    ).count()
    positive_urine_7d   = UrineTest.objects.filter(
        timestamp__gte=last_7d, protein_class__gte=3
    ).count()
    unresolved_alerts   = AlertLog.objects.filter(resolved=False).count()

    recent_alerts = AlertLog.objects.filter(resolved=False).values(
        'id', 'patient_name', 'village', 'gestational_week',
        'systolic', 'diastolic', 'protein_class', 'maps_url', 'timestamp'
    )[:10]

    return Response({
        'total_patients':    total_patients,
        'high_bp_today':     high_bp_today,
        'positive_urine_7d': positive_urine_7d,
        'unresolved_alerts': unresolved_alerts,
        'recent_alerts':     list(recent_alerts),
    })


@api_view(['PATCH'])
def resolve_alert(request, alert_id):
    """PATCH /api/alerts/<id>/resolve/"""
    try:
        alert = AlertLog.objects.get(id=alert_id)
        alert.resolved = True
        alert.save()
        return Response({'status': 'resolved'})
    except AlertLog.DoesNotExist:
        return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
