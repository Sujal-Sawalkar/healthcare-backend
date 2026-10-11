from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView

from .models import Patient
from .serializers import PatientSerializer


class PatientListCreateView(ListCreateAPIView):
    serializer_class = PatientSerializer

    def get_queryset(self):
        return Patient.objects.filter(created_by=self.request.user)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class PatientDetailView(RetrieveUpdateDestroyAPIView):
    serializer_class = PatientSerializer

    def get_queryset(self):
        # Other users' patients simply 404.
        return Patient.objects.filter(created_by=self.request.user)
