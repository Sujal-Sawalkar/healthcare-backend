from rest_framework import serializers

from doctors.serializers import DoctorSerializer

from .models import PatientDoctorMapping


class MappingSerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(source="patient.name", read_only=True)
    doctor_detail = DoctorSerializer(source="doctor", read_only=True)

    class Meta:
        model = PatientDoctorMapping
        fields = ("id", "patient", "patient_name", "doctor", "doctor_detail", "assigned_at")
        read_only_fields = ("id", "assigned_at")
        # Unique pair is checked in validate() for a friendlier message.
        validators = []

    def validate_patient(self, patient):
        if patient.created_by_id != self.context["request"].user.id:
            raise serializers.ValidationError("Patient not found.")
        return patient

    def validate(self, attrs):
        if PatientDoctorMapping.objects.filter(patient=attrs["patient"], doctor=attrs["doctor"]).exists():
            raise serializers.ValidationError("This doctor is already assigned to this patient.")
        return attrs
