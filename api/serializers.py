"""
API Serializers for PreeclampSense.
"""
from rest_framework import serializers
from preeclampsense.models import Patient, BPMeasurement, UrineTest, AlertLog


class BPMeasurementSerializer(serializers.ModelSerializer):
    class Meta:
        model = BPMeasurement
        fields = '__all__'


class UrineTestSerializer(serializers.ModelSerializer):
    protein_label = serializers.ReadOnlyField()

    class Meta:
        model = UrineTest
        fields = '__all__'


class AlertLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = AlertLog
        fields = '__all__'


class PatientSerializer(serializers.ModelSerializer):
    bp_measurements = BPMeasurementSerializer(many=True, read_only=True)
    urine_tests = UrineTestSerializer(many=True, read_only=True)

    class Meta:
        model = Patient
        fields = '__all__'
