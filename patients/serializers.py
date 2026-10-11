from rest_framework import serializers

from .models import Patient


class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = (
            "id", "name", "age", "gender", "phone", "address",
            "medical_history", "created_by", "created_at", "updated_at",
        )
        read_only_fields = ("id", "created_by", "created_at", "updated_at")

    def validate_name(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Name cannot be blank.")
        return value

    def validate_phone(self, value):
        if value and not (value.lstrip("+").isdigit() and 7 <= len(value.lstrip("+")) <= 15):
            raise serializers.ValidationError("Enter a valid phone number (7-15 digits).")
        return value
