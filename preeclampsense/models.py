# backend/preeclampsense/models.py
from django.db import models
from django.utils import timezone


class Patient(models.Model):
    name              = models.CharField(max_length=120)
    age               = models.IntegerField()
    gestational_week  = models.IntegerField()
    phone             = models.CharField(max_length=15)
    village           = models.CharField(max_length=120)
    created_at        = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.name} — Week {self.gestational_week}"


class BPMeasurement(models.Model):
    patient       = models.ForeignKey(Patient, on_delete=models.CASCADE,
                                      related_name='bp_measurements')
    timestamp     = models.DateTimeField(default=timezone.now)
    systolic      = models.FloatField()
    diastolic     = models.FloatField()
    heart_rate    = models.FloatField()
    spo2          = models.FloatField(default=98)
    risk_score    = models.FloatField(default=0)
    risk_level    = models.CharField(max_length=20, default='normal')

    class Meta:
        ordering = ['-timestamp']

    @property
    def is_high(self):
        return self.systolic >= 140 or self.diastolic >= 90


class UrineTest(models.Model):
    patient           = models.ForeignKey(Patient, on_delete=models.CASCADE,
                                          related_name='urine_tests')
    timestamp         = models.DateTimeField(default=timezone.now)
    protein_class     = models.IntegerField()   # 0=Neg 1=Trace 2=1+ 3=2+ 4=3+ 5=4+
    confidence        = models.FloatField()
    trigger_systolic  = models.FloatField()
    trigger_diastolic = models.FloatField()

    PROTEIN_LABELS = ['Negative', 'Trace', '1+', '2+', '3+', '4+']

    @property
    def protein_label(self):
        return self.PROTEIN_LABELS[min(self.protein_class, 5)]

    class Meta:
        ordering = ['-timestamp']


class AlertLog(models.Model):
    patient           = models.ForeignKey(Patient, on_delete=models.CASCADE,
                                          related_name='alerts', null=True, blank=True)
    timestamp         = models.DateTimeField(default=timezone.now)
    patient_name      = models.CharField(max_length=120)
    village           = models.CharField(max_length=120, blank=True)
    gestational_week  = models.IntegerField()
    systolic          = models.FloatField()
    diastolic         = models.FloatField()
    protein_class     = models.IntegerField()
    maps_url          = models.URLField(blank=True)
    resolved          = models.BooleanField(default=False)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"Alert: {self.patient_name} @ {self.timestamp:%Y-%m-%d %H:%M}"
