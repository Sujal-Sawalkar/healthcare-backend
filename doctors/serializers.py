from rest_framework import serializers

from .models import Doctor


class DoctorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Doctor
        fields = (
            "id", "name", "specialization", "email", "phone",
            "experience_years", "created_by", "created_at", "updated_at",
        )
        read_only_fields = ("id", "created_by", "created_at", "updated_at")

    def validate_email(self, value):
        value = value.lower()
        qs = Doctor.objects.filter(email__iexact=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("A doctor with this email already exists.")
        return value

    def validate_phone(self, value):
        if value and not (value.lstrip("+").isdigit() and 7 <= len(value.lstrip("+")) <= 15):
            raise serializers.ValidationError("Enter a valid phone number (7-15 digits).")
        return value
