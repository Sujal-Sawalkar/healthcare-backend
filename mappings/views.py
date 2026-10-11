from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.generics import ListCreateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from patients.models import Patient

from .models import PatientDoctorMapping
from .serializers import MappingSerializer


def user_mappings(user):
    return PatientDoctorMapping.objects.filter(patient__created_by=user).select_related("patient", "doctor")


class MappingListCreateView(ListCreateAPIView):
    """POST: assign doctor to patient. GET: all mappings for the user's patients."""

    serializer_class = MappingSerializer

    def get_queryset(self):
        return user_mappings(self.request.user)


class MappingDetailView(APIView):
    """
    GET    /api/mappings/<patient_id>/ -> doctors assigned to that patient
    DELETE /api/mappings/<id>/         -> remove a mapping
    (The spec uses the same URL shape for both, so <pk> means different things per method.)
    """

    def get(self, request, pk):
        patient = get_object_or_404(Patient, pk=pk, created_by=request.user)
        mappings = user_mappings(request.user).filter(patient=patient)
        return Response(MappingSerializer(mappings, many=True, context={"request": request}).data)

    def delete(self, request, pk):
        mapping = get_object_or_404(user_mappings(request.user), pk=pk)
        mapping.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
