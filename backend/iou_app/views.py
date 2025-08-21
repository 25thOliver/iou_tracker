from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import IOU
from .serializers import IOUSerializer

class IOUListCreateView(generics.ListCreateAPIView):
    serializer_class = IOUSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Return IOUs created by the current user"""
        return IOU.objects.filter(created_by=self.request.user)

    def perform_create(self, serializer):
        """Set the created_by field to the current user"""
        serializer.save(created_by=self.request.user)

class IOUDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = IOUSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'

    def get_queryset(self):
        """Return IOUs created by the current user"""
        return IOU.objects.filter(created_by=self.request.user)
